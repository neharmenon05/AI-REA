from fastapi import APIRouter
from pydantic import BaseModel

from backend.services.ner import SimpleNER
from backend.services.geocode import GeoService
from backend.services.amenities import AmenitiesService

router = APIRouter()

class PropertyRequest(BaseModel):
    query: str
    radius: int = 10000

class PropertyResponse(BaseModel):
    entities: dict
    lat: float
    lng: float
    amenities: dict

@router.post("/", response_model=PropertyResponse)
def get_property(req: PropertyRequest):
    ner = SimpleNER()
    entities = ner.extract(req.query)

    geo = GeoService()
    lat, lng, _ = geo.geocode(entities.get("location"))

    amenities_service = AmenitiesService()
    amenities = amenities_service.fetch_amenities(lat, lng, radius=req.radius)

    return PropertyResponse(entities=entities, lat=lat, lng=lng, amenities=amenities)
