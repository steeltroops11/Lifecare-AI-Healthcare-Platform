# Phase 4 — OpenStreetMap & OpenRouteService Service (Hardened Pass)
import time
import math
import json
import urllib.parse
import urllib.request
import os
import streamlit as st
from utils.logger import get_logger, safe_execute
from utils.ors_service import get_travel_times

logger = get_logger("utils.osm_service")

# ─────────────────────────────────────────────
# MODULE STATE FOR CIRCUIT BREAKER
# ─────────────────────────────────────────────
_ORS_CIRCUIT_BROKEN_UNTIL = 0.0  # Unix timestamp
CIRCUIT_BREAKER_COOLDOWN = 300.0  # 5 minutes deactivate duration

# ─────────────────────────────────────────────
# SPECIALTY KEYWORD MAP
# ─────────────────────────────────────────────
SPECIALTY_KEYWORDS = {
    "Cardiology":    ["heart", "cardiac", "cardio", "cardiovascular", "cardiology", "coronary"],
    "Endocrinology": ["diabetes", "endocrine", "endocrinology", "metabolic", "thyroid", "sugar", "insulin"],
    "Nephrology":    ["kidney", "renal", "nephro", "nephrology", "dialysis", "urology"],
    "General":       ["general", "multispeciality", "multi-specialty", "hospital", "clinic", "health", "medical"],
}

DISEASE_TO_SPECIALTY = {
    "Diabetes":      "Endocrinology",
    "Heart Disease": "Cardiology",
    "Kidney Disease": "Nephrology",
    "Readmission":   "General",
}


# ─────────────────────────────────────────────
# NOMINATIM GEOCODING (Wrapped safely)
# ─────────────────────────────────────────────
@safe_execute(fallback=(None, None), description="Nominatim City Geocoder")
def geocode_city(city_name: str, country: str = "India"):
    """Convert a city name to (lat, lng) using Nominatim (OpenStreetMap)."""
    if not city_name or not city_name.strip():
        return None, None

    logger.info(f"[GEOCIDING_REQUEST] query='{city_name.strip()}, {country}'")

    query = urllib.parse.urlencode({
        "q": f"{city_name.strip()}, {country}",
        "format": "json",
        "limit": 1,
    })
    url = f"https://nominatim.openstreetmap.org/search?{query}"
    
    # 2.5s Timeout for Nominatim
    req = urllib.request.Request(url, headers={"User-Agent": "HealthcareAnalyticsSystem/1.0"})
    with urllib.request.urlopen(req, timeout=2.5) as resp:
        data = json.loads(resp.read().decode())
        
    if data:
        lat, lng = float(data[0]["lat"]), float(data[0]["lon"])
        logger.info(f"[GEOCIDING_SUCCESS] query='{city_name.strip()}, {country}' lat='{lat}' lng='{lng}'")
        return lat, lng
    logger.warning(f"[GEOCIDING_FAIL] query='{city_name.strip()}, {country}' reason='No results found'")
    return None, None


# ─────────────────────────────────────────────
# OVERPASS API — BROAD HOSPITAL / CLINIC SEARCH
# ─────────────────────────────────────────────
def _build_overpass_query(lat: float, lng: float, radius_m: int) -> str:
    return f"""
    [out:json][timeout:25];
    (
      node["amenity"="hospital"](around:{radius_m},{lat},{lng});
      way["amenity"="hospital"](around:{radius_m},{lat},{lng});
      node["amenity"="clinic"](around:{radius_m},{lat},{lng});
      way["amenity"="clinic"](around:{radius_m},{lat},{lng});
      node["healthcare"="doctor"](around:{radius_m},{lat},{lng});
      node["healthcare"="hospital"](around:{radius_m},{lat},{lng});
      node["healthcare"="clinic"](around:{radius_m},{lat},{lng});
    );
    out center;
    """


def _parse_overpass_element(el: dict) -> dict:
    tags = el.get("tags", {})
    lat = el.get("lat") or el.get("center", {}).get("lat")
    lng = el.get("lon") or el.get("center", {}).get("lon")

    facility_type = "clinic"
    amenity = tags.get("amenity", tags.get("healthcare", ""))
    if amenity == "hospital":
        facility_type = "hospital"
    elif amenity == "doctor":
        facility_type = "doctor"

    return {
        "name":          tags.get("name") or tags.get("name:en") or "Unnamed Facility",
        "address":       _build_address(tags),
        "lat":           lat,
        "lng":           lng,
        "type":          facility_type,
        "phone":         tags.get("phone") or tags.get("contact:phone") or "",
        "website":       tags.get("website") or tags.get("contact:website") or "",
        "opening_hours": tags.get("opening_hours") or "",
        "osm_id":        el.get("id", ""),
        "specialty_score": 0,
    }


def _build_address(tags: dict) -> str:
    parts = []
    for key in ["addr:housenumber", "addr:street", "addr:suburb", "addr:city", "addr:state"]:
        v = tags.get(key)
        if v:
            parts.append(v)
    return ", ".join(parts) if parts else tags.get("addr:full", "")


@safe_execute(fallback=None, description="Overpass Facilities Broad Search")
def get_nearby_facilities(lat: float, lng: float, radius_km: float = 5.0) -> list:
    """Fetch hospitals, clinics, and doctors from Overpass API (with 2.5s connection timeout)."""
    logger.info(f"[OVERPASS_REQUEST] lat='{lat}' lng='{lng}' radius='{radius_km}'")
    radius_m = int(radius_km * 1000)
    query = _build_overpass_query(lat, lng, radius_m)
    url = "https://overpass-api.de/api/interpreter"
    
    encoded = urllib.parse.urlencode({"data": query}).encode()
    req = urllib.request.Request(url, data=encoded,
                                 headers={"Content-Type": "application/x-www-form-urlencoded",
                                          "User-Agent": "HealthcareAnalyticsSystem/1.0"})
    
    # 2.5s Timeout for connection setup (read timeout remains Overpass default)
    with urllib.request.urlopen(req, timeout=2.5) as resp:
        data = json.loads(resp.read().decode())

    elements = data.get("elements", [])
    facilities = []
    for el in elements:
        if el.get("tags") and el.get("tags").get("name"):
            f = _parse_overpass_element(el)
            if f["lat"] and f["lng"]:
                facilities.append(f)
    logger.info(f"[OVERPASS_SUCCESS] lat='{lat}' lng='{lng}' radius='{radius_km}' count='{len(facilities)}'")
    return facilities


# ─────────────────────────────────────────────
# AI SPECIALTY KEYWORD FILTER
# ─────────────────────────────────────────────
def filter_by_specialty(facilities: list, disease: str) -> list:
    """AI keyword filter sorting facilities based on disease specialty."""
    specialty = DISEASE_TO_SPECIALTY.get(disease, "General")
    keywords  = SPECIALTY_KEYWORDS.get(specialty, [])
    general_kw = SPECIALTY_KEYWORDS["General"]

    for f in facilities:
        score = 0
        searchable = (f["name"] + " " + f["website"] + " " + f["address"]).lower()
        for kw in keywords:
            if kw in searchable:
                score += 20
        for kw in general_kw:
            if kw in searchable:
                score += 5
                break
        if f["type"] == "hospital":
            score += 10
        f["specialty_score"] = score

    return sorted(facilities, key=lambda x: x["specialty_score"], reverse=True)


# ─────────────────────────────────────────────
# SEARCH RATE LIMITER
# ─────────────────────────────────────────────
def _is_rate_limited() -> bool:
    """Per-user rate limit validation (max 10 requests per minute)."""
    now = time.time()
    if "osm_rate_limit_timestamps" not in st.session_state:
        st.session_state["osm_rate_limit_timestamps"] = []
    
    # Clean timestamps older than 60 seconds
    st.session_state["osm_rate_limit_timestamps"] = [
        t for t in st.session_state["osm_rate_limit_timestamps"] if now - t < 60
    ]
    
    if len(st.session_state["osm_rate_limit_timestamps"]) >= 10:
        logger.warning("OSM Search Rate Limit hit (10 reqs/min exceeded).")
        return True
        
    st.session_state["osm_rate_limit_timestamps"].append(now)
    return False


# ─────────────────────────────────────────────
# OFFLINE EXPIRED CACHE LOOKUP
# ─────────────────────────────────────────────
def _get_expired_cache(cache_key: str):
    """Retrieve expired cache records regardless of fetched age (Offline Mode fallback)."""
    import sqlite3
    import utils.database as db
    try:
        conn = db.get_connection()
        row = conn.execute(
            "SELECT results_json FROM clinics_cache WHERE city_query = ? ORDER BY fetched_at DESC LIMIT 1",
            (cache_key,)
        ).fetchone()
        conn.close()
        if row:
            return json.loads(row[0])
    except Exception as e:
        logger.error(f"Failed to lookup expired cache: {str(e)}")
    return None


# ─────────────────────────────────────────────
# FULL PIPELINE (With Rate Limits & Offline fallbacks)
# ─────────────────────────────────────────────
def search_specialists(city: str, disease: str, radius_km: float = 5.0,
                       lat: float = None, lng: float = None, use_cache: bool = True):
    """
    Full geocode + cache + search pipeline.
    Implements offline fallback modes, rate limiting, and 2.5s connection timeouts.
    """
    import utils.database as db

    # 1. Rate Limiting Check
    if _is_rate_limited():
        st.warning("⚠️ Slow down! You have exceeded 10 searches per minute. Showing cached results if available.")

    # 2. Geocode city
    if not lat or not lng:
        lat, lng = geocode_city(city)
        if not lat:
            # Fallback to look up expired cache by city name
            expired_key = f"{city.lower().strip()}_{disease.lower().strip()}_{radius_km}"
            expired = _get_expired_cache(expired_key)
            if expired:
                st.info("🔌 Offline Mode: Network failed. Showing previously cached data.")
                logger.info(f"[CLINICS_CACHE_EXPIRED_HIT] key='{expired_key}' count={len(expired)}")
                return filter_by_specialty(expired, disease), None, None, True
            return [], None, None, False

    cache_key = f"{city.lower().strip()}_{disease.lower().strip()}_{radius_km}"

    # 3. Live cache check
    if use_cache:
        cached = db.get_cached_clinics(cache_key, int(radius_km))
        if cached:
            logger.info(f"[CLINICS_CACHE_HIT] key='{cache_key}' count='{len(cached)}'")
            return filter_by_specialty(cached, disease), lat, lng, True
        logger.info(f"[CLINICS_CACHE_MISS] key='{cache_key}'")
    else:
        logger.info(f"[CLINICS_CACHE_MISS] key='{cache_key}' reason='Cache bypassed'")

    # 4. Fetch live results from Overpass API (with 2.5s timeout)
    facilities = get_nearby_facilities(lat, lng, radius_km)
    
    # Try expanded radius if no results returned
    if not facilities:
        facilities = get_nearby_facilities(lat, lng, min(radius_km * 2, 20.0))

    if not facilities:
        # Offline Mode fallback: If Overpass API is down or network failed
        expired = _get_expired_cache(cache_key)
        if expired:
            st.info("🔌 Offline Mode: Overpass API unavailable. Loading expired cache.")
            logger.info(f"[CLINICS_CACHE_EXPIRED_HIT] key='{cache_key}' count={len(expired)}")
            return filter_by_specialty(expired, disease), lat, lng, True
        return [], lat, lng, False

    # 5. Save results to Cache
    if use_cache:
        try:
            db.cache_clinics(cache_key, lat, lng, int(radius_km), facilities)
        except Exception as e:
            logger.error(f"Failed caching results: {str(e)}")

    # 6. Apply specialty filter
    filtered = filter_by_specialty(facilities, disease)
    return filtered, lat, lng, False


# ─────────────────────────────────────────────
# OPENROUTESERVICE Travel ETA Calculator
# ─────────────────────────────────────────────
def get_travel_etas(lat1: float, lng1: float, lat2: float, lng2: float) -> dict:
    """
    Calculate Driving, Walking, and Cycling ETAs.
    Delegates to utils/ors_service while maintaining circuit breaker compatibility.
    """
    global _ORS_CIRCUIT_BROKEN_UNTIL
    
    from utils.hospital_ranker import haversine_km
    dist = haversine_km(lat1, lng1, lat2, lng2)

    driving_fallback = max(round(dist * 2.0 + 2), 1)
    cycling_fallback = max(round(dist * 4.0), 1)
    walking_fallback = max(round(dist * 12.0), 1)

    etas = {
        "driving": driving_fallback,
        "walking": walking_fallback,
        "cycling": cycling_fallback,
        "from_api": False
    }

    # 1. Circuit Breaker Check
    now = time.time()
    if now < _ORS_CIRCUIT_BROKEN_UNTIL:
        logger.warning(f"[ORS_CIRCUIT_BREAKER_ACTIVE] bypass_until='{_ORS_CIRCUIT_BROKEN_UNTIL}'")
        return etas

    # 2. Call new ORS Service
    res = get_travel_times(lat1, lng1, lat2, lng2)

    # 3. Trip Circuit Breaker if API key exists but request failed
    ors_key = os.environ.get("ORS_API_KEY") or os.environ.get("OPENROUTESERVICE_API_KEY")
    if not res.get("from_api", False) and ors_key:
        _ORS_CIRCUIT_BROKEN_UNTIL = now + CIRCUIT_BREAKER_COOLDOWN
        logger.warning(f"[ORS_CIRCUIT_BREAKER_TRIPPED] cooldown='{CIRCUIT_BREAKER_COOLDOWN}'")

    return {
        "driving": res["driving_minutes"],
        "walking": res["walking_minutes"],
        "cycling": res["cycling_minutes"],
        "from_api": res.get("from_api", False)
    }



# ─────────────────────────────────────────────
# GOOGLE MAPS & OSM URL BUILDERS
# ─────────────────────────────────────────────
def get_directions_url(name: str, lat: float = None, lng: float = None) -> str:
    """Build a Google Maps directions URL. No API key required."""
    if lat and lng:
        return f"https://www.google.com/maps/dir/?api=1&destination={lat},{lng}"
    encoded = urllib.parse.quote(f"{name}, India")
    return f"https://www.google.com/maps/search/?api=1&query={encoded}"


def get_osm_view_url(lat: float, lng: float) -> str:
    """Build an OpenStreetMap view URL for a location."""
    return f"https://www.openstreetmap.org/?mlat={lat}&mlon={lng}#map=15/{lat}/{lng}"


def get_static_map_url(lat: float, lng: float, zoom: int = 14) -> str:
    """Build a static OpenStreetMap embed URL (no API key needed)."""
    return (
        f"https://www.openstreetmap.org/export/embed.html"
        f"?bbox={lng-0.01},{lat-0.01},{lng+0.01},{lat+0.01}"
        f"&layer=mapnik&marker={lat},{lng}"
    )


@safe_execute(fallback=None, description="Nominatim Reverse Geocoder")
def reverse_geocode_coords(lat: float, lng: float) -> str:
    """Convert (lat, lng) to a city name using Nominatim."""
    url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lng}&format=json"
    req = urllib.request.Request(url, headers={"User-Agent": "HealthcareAnalyticsSystem/1.0"})
    with urllib.request.urlopen(req, timeout=2.5) as resp:
        data = json.loads(resp.read().decode())
    if data and "address" in data:
        addr = data["address"]
        return addr.get("city") or addr.get("town") or addr.get("village") or addr.get("suburb") or addr.get("state_district") or addr.get("state")
    return None
