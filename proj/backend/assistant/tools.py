"""
tools.py ─ Tools tailored to AI-REA's actual backend structure.

Your backend has ONE unified endpoint: POST /api/analyze
So we only need a few focused tools.
"""

import json
import os
import httpx
from langchain_core.tools import tool

BACKEND_BASE = os.getenv("AI_REA_BACKEND_URL", "http://localhost:8000")


# ════════════════════════════════════════════════════════════════════
#  HELPER
# ════════════════════════════════════════════════════════════════════
def _post_sync(path: str, body: dict) -> dict:
    """Synchronous HTTP POST — LangGraph tools must be sync."""
    with httpx.Client(timeout=60) as c:  # 60s timeout for full analysis
        r = c.post(f"{BACKEND_BASE}{path}", json=body)
        r.raise_for_status()
        return r.json()


# ════════════════════════════════════════════════════════════════════
#  UI TOOLS  ─  instructions the frontend executes
# ════════════════════════════════════════════════════════════════════

@tool
def guide_to_page(page: str) -> str:
    """Navigate the user to a specific page of the AI-REA website.
    Use when they ask 'where is X', 'how do I analyze', 'show me dashboard', etc.

    Args:
        page: Which page. One of: dashboard, results, marketplace, about
    """
    return json.dumps({
        "ui_action": "guide",
        "page": page,
    })


@tool
def fill_query_input(query: str) -> str:
    """Auto-fill the dashboard query input box with a property description.
    Use when the user describes a property in chat and you want to save them
    the effort of re-typing it in the form.

    Args:
        query: Natural language property description, e.g. "3 BHK in Kharadi Pune 1500 sqft"
    """
    return json.dumps({
        "ui_action": "fill_query",
        "query": query,
    })


# ════════════════════════════════════════════════════════════════════
#  DATA TOOL  ─  calls your actual backend
# ════════════════════════════════════════════════════════════════════

@tool
def run_property_analysis(query: str, radius: int = 10000) -> str:
    """Run a full property analysis using AI-REA's backend.
    This calls the same endpoint the dashboard uses: /api/analyze
    
    Returns: estimated price, forecast, risk assessment, amenities, news, AI explanation
    
    Use when the user wants to analyze a property AND you have a complete
    description from them. The query must include location, size, and ideally BHK.
    
    Args:
        query: Natural language property query, e.g. "3 BHK apartment in Kharadi Pune, 1500 sqft"
        radius: Search radius in meters for amenities (default 10000 = 10km)
    """
    try:
        result = _post_sync("/api/analyze/", {
            "query": query,
            "radius": radius
        })
        
        # Return a clean summary the LLM can work with
        # Full result has: summary, forecast, risk, estimated_current_price,
        # location, amenities, news, explanation
        
        return json.dumps({
            "success": True,
            "summary": result.get("summary"),
            "current_price": result.get("estimated_current_price"),
            "price_per_sqft": result.get("price_per_sqft"),
            "forecast_5yr": result.get("forecast", {}).get("5"),
            "risk": result.get("risk"),
            "risk_explanation": result.get("risk_explanation"),
            "amenity_count": result.get("forecast_details", {}).get("amenity_count", 0),
            "news_sentiment": result.get("forecast_details", {}).get("news_score", 0),
            "explanation": result.get("explanation"),
            "location": result.get("location"),
        })
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e)
        })

@tool
def fill_sell_property_form(
    title: str = "",
    location: str = "",
    sublocality: str = "",
    property_type: str = "",
    bhk: str = "",
    size: str = "",
    floor: str = "",
    total_floors: str = "",
    property_age: str = "",
    price: str = "",
    furnishing: str = "",
    parking: str = "",
    description: str = "",
    owner_name: str = "",
    owner_phone: str = "",
    owner_email: str = ""
) -> str:
    """Auto-fill the 'List Your Property' form when user describes their property.
    Use when the user is on the marketplace/sell page and mentions property details.
    Only fill fields the user actually mentioned - leave others empty.
    
    Args:
        title: Property title/heading
        location: City name
        sublocality: Locality/neighborhood
        property_type: One of: Apartment, House, Villa, Other
        bhk: One of: 1 BHK, 2 BHK, 3 BHK, 4+ BHK, Other
        size: Area in sqft (as string)
        floor: Floor number
        total_floors: Total floors in building
        property_age: Age in years
        price: Property price
        furnishing: One of: Fully Furnished, Semi Furnished, Unfurnished, Other
        parking: Number of parking spaces
        description: Property description text
        owner_name: Owner's name
        owner_phone: Owner's phone
        owner_email: Owner's email
    """
    fields = {}
    if title: fields["title"] = title
    if location: fields["location"] = location
    if sublocality: fields["sublocality"] = sublocality
    if property_type: fields["property_type"] = property_type
    if bhk: fields["bhk"] = bhk
    if size: fields["size"] = size
    if floor: fields["floor"] = floor
    if total_floors: fields["total_floors"] = total_floors
    if property_age: fields["property_age"] = property_age
    if price: fields["price"] = price
    if furnishing: fields["furnishing"] = furnishing
    if parking: fields["parking"] = parking
    if description: fields["description"] = description
    if owner_name: fields["owner_name"] = owner_name
    if owner_phone: fields["owner_phone"] = owner_phone
    if owner_email: fields["owner_email"] = owner_email
    
    return json.dumps({
        "ui_action": "fill_sell_form",
        "fields": fields,
    })


@tool
def generate_property_description(
    property_type: str,
    bhk: str,
    location: str,
    size: str,
    key_features: str = ""
) -> str:
    """Generate a professional property description for listings.
    Use when the user asks for help writing a description for their property listing.
    
    Args:
        property_type: Type of property (Apartment, House, Villa, etc.)
        bhk: Number of bedrooms (1 BHK, 2 BHK, etc.)
        location: City and locality
        size: Area in sqft
        key_features: Any special features mentioned by user (optional)
    """
    # Generate description based on inputs
    desc_parts = []
    
    desc_parts.append(f"Spacious {bhk} {property_type.lower()} available in {location}.")
    desc_parts.append(f"Property spans {size} sqft with well-designed interiors.")
    
    if key_features:
        desc_parts.append(key_features)
    
    desc_parts.append("Ideal for families looking for a comfortable living space.")
    desc_parts.append("Contact owner for viewing and more details.")
    
    generated = " ".join(desc_parts)
    
    return json.dumps({
        "success": True,
        "description": generated,
        "suggestion": "You can use this as-is or modify it to add more personal details."
    })

# ─── all tools for LangGraph ──────────────────────────────────────
ALL_TOOLS = [
    guide_to_page,
    fill_query_input,
    fill_sell_property_form,
    generate_property_description,
    run_property_analysis,
]
