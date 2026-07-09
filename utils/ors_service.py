import os
import time
import json
import urllib.request
import urllib.parse
import math
from dotenv import load_dotenv
from utils.logger import get_logger

# Load env variables
load_dotenv()

logger = get_logger("utils.ors_service")

def haversine_km(lat1, lon1, lat2, lon2):
    """Calculate the great-circle distance between two points in kilometers."""
    R = 6371.0  # Radius of the earth in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def get_travel_times(origin_lat, origin_lon, destination_lat, destination_lon):
    """
    Calculate driving, walking, and cycling times in minutes using OpenRouteService.
    Falls back to straight-line estimations if API key is missing or request fails.
    """
    # 1. Straight-line fallback calculations using our self-contained haversine formula
    dist = haversine_km(origin_lat, origin_lon, destination_lat, destination_lon)

    driving_fallback = max(round(dist * 2.0 + 2), 1)
    cycling_fallback = max(round(dist * 4.0), 1)
    walking_fallback = max(round(dist * 12.0), 1)

    fallback_res = {
        "driving_minutes": driving_fallback,
        "walking_minutes": walking_fallback,
        "cycling_minutes": cycling_fallback,
        "from_api": False
    }

    # 2. Fetch API Key
    ors_key = os.getenv("ORS_API_KEY") or os.getenv("OPENROUTESERVICE_API_KEY")
    if not ors_key:
        logger.info(f"[ORS_MISSING_KEY] origin='{origin_lat},{origin_lon}' destination='{destination_lat},{destination_lon}'")
        return fallback_res

    # 3. Request URL Construction
    url = f"https://api.openrouteservice.org/v2/directions/driving-car?start={origin_lon},{origin_lat}&end={destination_lon},{destination_lat}"
    req = urllib.request.Request(url, headers={
        "Authorization": ors_key,
        "User-Agent": "HealthcareAnalyticsSystem/1.0"
    })

    # 4. Retry Loop with 3.0s Timeout
    success = False
    data = None
    t0 = time.time()
    
    for attempt in range(2):
        try:
            logger.info(f"[ORS_API_REQUEST] origin='{origin_lat},{origin_lon}' destination='{destination_lat},{destination_lon}' attempt={attempt+1}")
            with urllib.request.urlopen(req, timeout=3.0) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode())
                    success = True
                    dt = time.time() - t0
                    logger.info(f"[ORS_API_SUCCESS] origin='{origin_lat},{origin_lon}' destination='{destination_lat},{destination_lon}' duration_sec='{dt:.3f}'")
                    break
                else:
                    raise Exception(f"HTTP status code {response.status}")
        except Exception as e:
            if attempt == 0:
                logger.warning(f"[ORS_API_RETRY] origin='{origin_lat},{origin_lon}' destination='{destination_lat},{destination_lon}' attempt='1' error='{str(e)}'")
                time.sleep(1.0)
                continue
            else:
                logger.error(f"[ORS_API_FAIL] origin='{origin_lat},{origin_lon}' destination='{destination_lat},{destination_lon}' error='{str(e)}'")

    if not success or not data:
        return fallback_res

    # 5. Parse summary duration
    try:
        features = data.get("features", [])
        if features:
            properties = features[0].get("properties", {})
            summary = properties.get("summary", {})
            duration_sec = summary.get("duration", 0)
            if duration_sec > 0:
                driving_mins = max(round(duration_sec / 60.0), 1)
                return {
                    "driving_minutes": driving_mins,
                    "walking_minutes": max(round(driving_mins * 6.0), 1),
                    "cycling_minutes": max(round(driving_mins * 2.0), 1),
                    "from_api": True
                }
    except Exception as e:
        logger.error(f"[ORS_PARSE_FAIL] error='{str(e)}'")

    return fallback_res
