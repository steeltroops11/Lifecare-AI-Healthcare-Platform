# API Documentation

This system utilizes public mapping endpoints and routing services to construct coordinates, hospitals, and transit travel durations.

## Integrations

### 1. Nominatim Geocoding API
* **Provider**: OpenStreetMap (OSM)
* **Endpoint**: `https://nominatim.openstreetmap.org/search`
* **Purpose**: Resolves a city name (e.g. `"New Delhi"`) into GPS latitude and longitude.
* **Headers**: Requires a custom `User-Agent` (`HealthcareAnalyticsSystem/1.0`) to comply with OSM usage guidelines.
* **Authentication**: None.

### 2. Overpass API
* **Provider**: OpenStreetMap (OSM)
* **Endpoint**: `https://overpass-api.de/api/interpreter`
* **Purpose**: Fetches nearby hospitals, clinics, and doctors within a specific radius of coordinates.
* **Query Format**: Overpass QL (Query Language). Query filters for `amenity="hospital"`, `amenity="clinic"`, and `healthcare="doctor"`.
* **Authentication**: None.

### 3. OpenRouteService Directions API
* **Provider**: OpenRouteService (ORS)
* **Endpoint**: `https://api.openrouteservice.org/v2/directions/driving-car`
* **Purpose**: Fetches driving duration, which is then utilized to compute proportional cycling and walking ETAs.
* **Authentication**: **API Key needed**. Must be supplied as an HTTP header:
  `Authorization: <YOUR_API_KEY>`
* **Limits**: 40 requests/minute (Free tier limit). To prevent exceeding this limit, the system calls this API only for the top 3 ranked hospitals.

### 4. Google Maps Search & Directions URLs
* **Endpoint**: `https://www.google.com/maps/dir/?api=1`
* **Purpose**: Opens Google Maps navigation in a separate browser tab to guide the patient to the hospital.
* **Authentication**: None.
