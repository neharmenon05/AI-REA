import os
import requests
from dotenv import load_dotenv
load_dotenv()

GOOGLE_PLACES_NEARBY_URL = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"

class AmenitiesService:
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_PLACES_API_KEY")
        # Allow running in dev without API key; functions will return notes instead.
        self.enabled = bool(self.api_key)

    def fetch_amenities(self, lat: float, lng: float, radius: int = 10000):
        amenity_types = {
            "schools": "school",
            "hospitals": "hospital",
            "parks": "park",
            "metro_stations": "transit_station",
            "malls": "shopping_mall",
            "restaurants": "restaurant",
            "banks": "bank",
            "gyms": "gym",
            "pharmacies": "pharmacy",
            "colleges": "university"
        }
        if not self.enabled:
            return {"note": "Google Places not configured — amenities unavailable in development"}

        out = {}
        session = requests.Session()
        for label, ptype in amenity_types.items():
            params = {"location": f"{lat},{lng}", "radius": radius, "type": ptype, "key": self.api_key}
            r = session.get(GOOGLE_PLACES_NEARBY_URL, params=params, timeout=20)
            r.raise_for_status()
            data = r.json()
            results = data.get("results", [])
            out[label] = {"count": len(results), "names": [p.get("name") for p in results], "places": results}
        return out
