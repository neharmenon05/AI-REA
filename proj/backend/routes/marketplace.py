import os, uuid, json
from fastapi import APIRouter, Form, UploadFile, HTTPException
from typing import List
from supabase import create_client, Client
from dotenv import load_dotenv

# ---------------- Load ENV ----------------
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path)

router = APIRouter(prefix="/api/marketplace", tags=["Marketplace"])

# ---------------- Supabase ----------------
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise Exception("Supabase credentials missing")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


# ---------------- SUBMIT PROPERTY ----------------
@router.post("/submit")
async def submit(
    title: str = Form(...),
    description: str = Form(""),
    location: str = Form(...),
    sublocality: str = Form(...),
    property_type: str = Form(...),
    bhk: str = Form(...),
    size: float = Form(...),
    floor: str = Form(None),
    total_floors: str = Form(None),
    property_age: str = Form(None),
    price: float = Form(...),
    furnishing_status: str = Form(None),
    parking: str = Form("0"),
    owner_name: str = Form(...),
    owner_phone: str = Form(...),
    owner_email: str = Form(...),
    amenities: str = Form("{}"),
    images: List[UploadFile] = None
):
    try:
        # Safe conversion helpers
        def to_int(val):
            return int(val) if val and val.strip() != "" else None

        def to_float(val):
            return float(val) if val and val.strip() != "" else None

        floor_val = to_int(floor)
        total_floors_val = to_int(total_floors)
        property_age_val = to_int(property_age)
        parking_val = to_int(parking)

        # Upload images
        image_urls = []
        if images:
            for img in images:
                ext = img.filename.split(".")[-1]
                name = f"{uuid.uuid4()}.{ext}"
                file_bytes = await img.read()
                supabase.storage.from_("property-images").upload(name, file_bytes)
                public_url = supabase.storage.from_("property-images").get_public_url(name)
                image_urls.append(public_url)

        supabase.table("properties").insert({
            "title": title,
            "description": description,
            "location": location,
            "sublocality": sublocality,
            "property_type": property_type,
            "bhk": bhk,
            "size": size,
            "price": price,
            "price_per_sqft": price/size if size else None,
            "furnishing_status": furnishing_status,
            "parking": parking_val,
            "owner_name": owner_name,
            "owner_phone": owner_phone,
            "owner_email": owner_email,
            "amenities": json.loads(amenities),
            "images": image_urls,
            "status": "active",
            "floor": floor_val,
            "total_floors": total_floors_val,
            "property_age": property_age_val
        }).execute()

        return {"message": "Property submitted successfully"}
    except Exception as e:
        raise HTTPException(500, detail=str(e))
    
@router.get("/properties")
def get_properties():
    try:
        response = supabase.table("properties").select("*").eq("status", "active").execute()
        data = response.data
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))