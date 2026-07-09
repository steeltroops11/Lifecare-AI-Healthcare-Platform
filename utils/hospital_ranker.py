# Phase 4 — Hospital Ranking Engine (M5) + Hospital Intelligence AI Best-Pick (M9)
# Revised weights: Distance 45%, Type 35%, Website+Phone 10%, Specialty match 10%
# OSM has no ratings — we do NOT use ratings in scoring.

import math

# ─────────────────────────────────────────────
# HAVERSINE DISTANCE
# ─────────────────────────────────────────────
def haversine_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Calculate the great-circle distance in km between two GPS coordinates."""
    R = 6371  # Earth radius km
    d_lat = math.radians(lat2 - lat1)
    d_lng = math.radians(lng2 - lng1)
    a = (math.sin(d_lat / 2) ** 2
         + math.cos(math.radians(lat1))
         * math.cos(math.radians(lat2))
         * math.sin(d_lng / 2) ** 2)
    return R * 2 * math.asin(math.sqrt(a))


# ─────────────────────────────────────────────
# DISTANCE SCORE (45% weight)
# ─────────────────────────────────────────────
def _distance_score(distance_km: float) -> float:
    """Convert distance to a 0–100 score. Closer = higher."""
    if distance_km <= 1:
        return 100
    elif distance_km <= 3:
        return 80
    elif distance_km <= 5:
        return 60
    elif distance_km <= 10:
        return 40
    elif distance_km <= 20:
        return 20
    else:
        return 0


# ─────────────────────────────────────────────
# FACILITY TYPE SCORE (35% weight)
# ─────────────────────────────────────────────
def _type_score(facility_type: str) -> float:
    """Score based on facility type. Hospitals score highest."""
    return {
        "hospital": 100,
        "clinic":   75,
        "doctor":   50,
    }.get(facility_type.lower(), 50)


# ─────────────────────────────────────────────
# WEBSITE SCORE (5% weight)
# ─────────────────────────────────────────────
def _website_score(website: str) -> float:
    """Score based on whether facility has an official website."""
    return 100 if (website and website.strip() and website.startswith("http")) else 0


# ─────────────────────────────────────────────
# PHONE SCORE (5% weight)
# ─────────────────────────────────────────────
def _phone_score(phone: str) -> float:
    """Score based on whether facility has a contact number."""
    return 100 if (phone and len(phone.strip()) > 5) else 0


# ─────────────────────────────────────────────
# SPECIALTY MATCH SCORE (10% weight)
# Based on AI keyword matching from osm_service.py
# ─────────────────────────────────────────────
def _specialty_score(facility: dict) -> float:
    """Use pre-calculated specialty_score from AI keyword filter (0–100 normalized)."""
    raw = facility.get("specialty_score", 0)
    # Normalize: max expected raw score ~60 (3 keyword matches × 20)
    return min((raw / 60) * 100, 100)


# ─────────────────────────────────────────────
# RISK-TIER BASED FACILITY FILTERING
# ─────────────────────────────────────────────
def filter_by_risk_tier(facilities: list, risk_level: str) -> list:
    """
    Filter facilities based on risk level:
    CRITICAL → hospitals only (no small clinics)
    HIGH     → hospitals preferred + clinics
    MODERATE → both hospitals and clinics
    LOW      → clinics and doctors only
    """
    if risk_level == "CRITICAL":
        filtered = [f for f in facilities if f.get("type") == "hospital"]
        return filtered if filtered else facilities  # fallback to all if no hospitals found

    elif risk_level == "HIGH":
        # Show hospitals first, then clinics
        hospitals = [f for f in facilities if f.get("type") == "hospital"]
        others    = [f for f in facilities if f.get("type") != "hospital"]
        return hospitals + others

    elif risk_level == "MODERATE":
        return facilities  # show all

    else:  # LOW
        small = [f for f in facilities if f.get("type") in ["clinic", "doctor"]]
        return small if small else facilities  # fallback if no clinics found


# ─────────────────────────────────────────────
# MAIN RANKING FUNCTION
# ─────────────────────────────────────────────
def rank_hospitals(facilities: list, user_lat: float, user_lng: float,
                   disease: str = "", risk_level: str = "MODERATE") -> list:
    """
    Score and rank all facilities.
    Applies risk-tier filtering before ranking.

    Weights:
      Distance:   40%
      Specialty:  25%
      Type:       20%
      Phone:      10%
      Website:    5%

    Returns sorted list with added fields: distance_km, total_score, rank, travel_etas
    """
    # Apply risk-tier filter
    filtered = filter_by_risk_tier(facilities, risk_level)

    ranked = []
    for f in filtered:
        lat = f.get("lat")
        lng = f.get("lng")
        if not lat or not lng:
            continue

        dist_km = haversine_km(user_lat, user_lng, lat, lng)
        d_score = _distance_score(dist_km)
        t_score = _type_score(f.get("type", "clinic"))
        w_score = _website_score(f.get("website", ""))
        p_score = _phone_score(f.get("phone", ""))
        s_score = _specialty_score(f)

        # New Phase 4 Weights
        total = (
            d_score * 0.40
            + s_score * 0.25
            + t_score * 0.20
            + p_score * 0.10
            + w_score * 0.05
        )

        ranked.append({
            **f,
            "distance_km": round(dist_km, 2),
            "total_score": round(total, 1),
            "score_breakdown": {
                "distance": round(d_score, 1),
                "specialty": round(s_score, 1),
                "type":     round(t_score, 1),
                "phone":    round(p_score, 1),
                "website":  round(w_score, 1),
            }
        })

    # Sort by total score descending, then distance ascending as tiebreaker
    ranked.sort(key=lambda x: (-x["total_score"], x["distance_km"]))

    # Add rank badge and compute ETAs
    from utils.osm_service import get_travel_etas
    for i, f in enumerate(ranked):
        f["rank"] = i + 1
        lat = f.get("lat")
        lng = f.get("lng")
        
        # Performance optimization: call ORS API (via get_travel_etas) only for top 3 to prevent rate limits.
        # Fallback to straight-line velocity calculations for the rest.
        if i < 3:
            f["travel_etas"] = get_travel_etas(user_lat, user_lng, lat, lng)
        else:
            # Inline fast fallback calculation to avoid network overhead
            dist = f["distance_km"]
            f["travel_etas"] = {
                "driving": max(round(dist * 2.0 + 2), 1),
                "walking": max(round(dist * 12.0), 1),
                "cycling": max(round(dist * 4.0), 1),
                "from_api": False
            }

    return ranked


# ─────────────────────────────────────────────
# M9 — HOSPITAL INTELLIGENCE ENGINE
# AI chooses the single BEST hospital with explanation
# ─────────────────────────────────────────────
def get_ai_best_pick(ranked_facilities: list, disease: str) -> dict | None:
    """
    Select the single best hospital from ranked list.
    Returns the top facility with an AI-generated explanation & score breakdown.
    """
    if not ranked_facilities:
        return None

    best = ranked_facilities[0]
    breakdown = best.get("score_breakdown", {})
    dist = best.get("distance_km", 0)
    ftype = best.get("type", "facility").capitalize()
    score = best.get("total_score", 0)
    name = best.get("name", "This facility")

    reasons = []
    
    # Distance breakdown
    d_pt = round(breakdown.get("distance", 0) * 0.40, 1)
    if breakdown.get("distance", 0) >= 80:
        reasons.append(f"Closest Location (+{d_pt} pts, {dist} km)")
    else:
        reasons.append(f"Location (+{d_pt} pts, {dist} km)")

    # Specialty breakdown
    s_pt = round(breakdown.get("specialty", 0) * 0.25, 1)
    if s_pt > 0:
        reasons.append(f"Specialty Match (+{s_pt} pts)")

    # Type breakdown
    t_pt = round(breakdown.get("type", 0) * 0.20, 1)
    reasons.append(f"{ftype} Facility (+{t_pt} pts)")

    # Phone breakdown
    p_pt = round(breakdown.get("phone", 0) * 0.10, 1)
    if p_pt > 0:
        reasons.append(f"Contact Info Available (+{p_pt} pts)")

    # Website breakdown
    w_pt = round(breakdown.get("website", 0) * 0.05, 1)
    if w_pt > 0:
        reasons.append(f"Official Website (+{w_pt} pts)")

    reason_str = " | ".join(reasons)

    best["ai_explanation"] = (
        f"🎯 **AI Best Match Reason**: {reason_str}"
    )
    best["is_ai_pick"] = True

    return best
