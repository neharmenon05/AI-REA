import os
import requests
from dotenv import load_dotenv
load_dotenv()

GOOGLE_GEOCODE_URL = "https://maps.googleapis.com/maps/api/geocode/json"

class GeoService:
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_PLACES_API_KEY")
        # Do not raise on missing key during development; allow graceful degradation.
        if not self.api_key:
            # service disabled flag
            self.enabled = False
        else:
            self.enabled = True

    def geocode(self, location: str):
        if not self.enabled:
            # return None to indicate geocoding not available
            return None

        params = {"address": location, "key": self.api_key}
        r = requests.get(GOOGLE_GEOCODE_URL, params=params, timeout=20)
        r.raise_for_status()
        data = r.json()
        if data.get("status") != "OK" or not data.get("results"):
            raise RuntimeError(f"Geocoding failed: {data}")
        loc = data["results"][0]["geometry"]["location"]
        return loc["lat"], loc["lng"], data["results"][0]
