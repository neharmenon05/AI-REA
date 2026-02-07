from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from backend.services.ner import SimpleNER
from backend.services.geocode import GeoService
from backend.services.amenities import AmenitiesService
from backend.services.news_service import NewsService
from backend.services.forecaster import TinyLSTMForecaster
from backend.services.gemini_wrapper import GeminiWrapper

router = APIRouter()

class AnalyzeRequest(BaseModel):
    query: str
    radius: int = 10000

class AnalyzeResponse(BaseModel):
    summary: str
    forecast: dict
    risk: str
    risk_explanation: Optional[str] = None
    estimated_current_price: Optional[float] = None
    base_price: Optional[float] = None
    price_per_sqft: Optional[float] = None
    serp_average: Optional[float] = None
    amenity_boost_pct: Optional[float] = None
    news_impact_pct: Optional[float] = None
    location: dict
    amenities: dict
    news: list
    explanation: str
    forecast_details: Optional[dict] = None
    methodology: Optional[str] = None

@router.post("/", response_model=AnalyzeResponse)
def analyze_property(req: AnalyzeRequest):
    """
    Professional property analysis endpoint
    
    Workflow:
    1. Extract entities (city, area, BHK, sqft) using NER
    2. Geocode location to get lat/lng
    3. Fetch nearby amenities (weighted scoring)
    4. Search relevant news (sentiment analysis)
    5. Run LSTM forecaster with full context
    6. Compute risk assessment
    7. Generate AI explanation
    8. Return structured response
    """
    
    try:
        print(f"\n{'='*70}")
        print(f" PROPERTY ANALYSIS REQUEST: {req.query}")
        print(f"{'='*70}\n")
        
        # STEP 1: Extract Entities from Query
        ner = SimpleNER()
        entities = ner.extract(req.query)
        
        city = entities.get("city") or entities.get("location") or "Mumbai"
        area = entities.get("area")
        bhk = entities.get("bhk") or 2
        size_sqft = entities.get("size_sqft") or 1000
        
        print(f"Extracted entities:")
        print(f"    City: {city}")
        print(f"    Area: {area or 'Not specified'}")
        print(f"    BHK: {bhk}")
        print(f"    Size: {size_sqft} sqft\n")
        
        # STEP 2: Geocode Location
        lat = lng = None
        loc_data = {}
        try:
            geo = GeoService()
            location_str = f"{area}, {city}" if area else city
            geo_res = geo.geocode(location_str)
            if geo_res:
                lat, lng, loc_data = geo_res
                print(f" Geocoded: {location_str} → ({lat:.4f}, {lng:.4f})\n")
            else:
                print(f" Geocoding failed for: {location_str}\n")
        except Exception as e:
            print(f" Geocoding error: {e}\n")
            lat, lng, loc_data = None, None, {}

        # STEP 3: Fetch Amenities
        amenities = {}
        try:
            if lat is not None and lng is not None:
                amenities_service = AmenitiesService()
                amenities = amenities_service.fetch_amenities(lat, lng, radius=req.radius)
                amenity_count = sum(
                    len(v.get('places', [])) if isinstance(v, dict) and 'places' in v else 0
                    for v in amenities.values()
                )
                print(f" Fetched amenities: {amenity_count} total facilities\n")
            else:
                amenities = {"note": "Amenities skipped — no geolocation available"}
                print(f" Skipping amenities: No geolocation\n")
        except Exception as e:
            print(f" Amenities fetch error: {e}\n")
            amenities = {"error": str(e)}

        # STEP 4: Search News
        news_results = []
        try:
            news_service = NewsService()
            location_str = f"{area}, {city}" if area else city
            news_query = f"{location_str} real estate development infrastructure"
            news_results = news_service.search_news(news_query, num=10)
            
            if not news_results:
                news_results = [{"note": "No news items found for this location."}]
                print(f"ℹ No news found for: {news_query}\n")
            else:
                valid_news = [n for n in news_results if isinstance(n, dict) and 'error' not in n and 'note' not in n]
                print(f" Fetched news: {len(valid_news)} relevant articles\n")
        except Exception as e:
            print(f" News search error: {e}\n")
            news_results = [{"error": str(e)}]

        # STEP 5: Run Forecaster with Full Context
        forecast_data = {}
        estimated_current_price = None
        base_price = None
        price_per_sqft = None
        serp_average = None
        amenity_boost_pct = None
        news_impact_pct = None
        forecast_explanation = ""
        methodology = "LSTM with weighted amenities and news sentiment"
        
        try:
            forecaster = TinyLSTMForecaster()
            
            # Use forecast_with_context for comprehensive analysis
            forecast_data = forecaster.forecast_with_context(
                city=city,
                area=area,
                bhk=bhk,
                sqft=size_sqft,
                amenities=amenities,
                news=news_results,
                query_text=req.query,
                years_to_forecast=[2, 3, 5, 10]
            )
            
            # Extract all data from forecast
            forecast_price = forecast_data.get('predictions', {})
            estimated_current_price = forecast_data.get('current_price')
            base_price = forecast_data.get('base_price')
            price_per_sqft = forecast_data.get('price_per_sqft')
            serp_average = forecast_data.get('serp_average')
            amenity_boost_pct = forecast_data.get('amenity_boost_pct')
            news_impact_pct = forecast_data.get('news_impact_pct')
            forecast_explanation = forecast_data.get('explanation', '')
            methodology = forecast_data.get('methodology', methodology)
            
            print(f" Forecast complete: Current ₹{estimated_current_price:,.0f}, 5yr ₹{forecast_data.get('predicted_5', 0):,.0f}\n")
            
        except Exception as e:
            print(f" Forecaster error: {e}\n")
            # Fallback forecast
            fallback_base = bhk * size_sqft * 2000  # ₹2000/sqft default
            estimated_current_price = fallback_base
            base_price = fallback_base
            price_per_sqft = 2000.0
            forecast_price = {
                "2": float(fallback_base * 1.12),
                "3": float(fallback_base * 1.18),
                "5": float(fallback_base * 1.30),
                "10": float(fallback_base * 1.65),
                "note": "Fallback forecast used due to processing error"
            }
            forecast_explanation = "Conservative growth estimates applied due to data limitations."

        # STEP 6: Compute Risk Assessment
        risk, risk_explanation = _compute_risk_assessment(
            news_results=news_results,
            amenities=amenities,
            forecast_data=forecast_data,
            city=city,
            area=area
        )
        
        print(f" Risk assessment: {risk}")
        print(f"   {risk_explanation}\n")

        # STEP 7: Generate Comprehensive Explanation
        try:
            explanation = forecast_explanation

            if not explanation or len(str(explanation).strip()) < 50:
                gem = GeminiWrapper()
                
                # Safe value extraction
                location_str = f"{area}, {city}" if area else (city if city else "the area")
                current_price = float(estimated_current_price) if estimated_current_price else 0
                price_sqft = float(price_per_sqft) if price_per_sqft else 0
                amenity_pct = float(amenity_boost_pct) if amenity_boost_pct is not None else 0
                news_pct = float(news_impact_pct) if news_impact_pct is not None else 0
                forecast_5yr = float(forecast_data.get('predicted_5', current_price * 1.2)) if forecast_data.get('predicted_5') else current_price * 1.2
                inv_score = float(forecast_data.get('score', 0.5)) if forecast_data.get('score') is not None else 0.5
                bhk_val = bhk if bhk else 2
                size_val = size_sqft if size_sqft else 1000
                risk_val = risk if risk else "Moderate"

                prompt = f'''Provide a professional real estate investment analysis.

Property: {bhk_val} BHK, {size_val} sqft in {location_str}
Current price: Rs {current_price:,.0f} (Rs {price_sqft:,.0f}/sqft)
Amenities impact: {amenity_pct:.1f}%
News impact: {news_pct:+.1f}%
Risk Level: {risk_val}
5-Year Forecast: Rs {forecast_5yr:,.0f}
Investment Score: {inv_score:.2f}/1.0

Explain outlook, drivers, and risks in one paragraph.'''

                explanation = gem.generate_explanation(prompt, debug=True)

                if not explanation or len(explanation.strip()) < 20:
                    raise ValueError("Insufficient response from Gemini")

        except Exception as e:
            print(f"WARNING STEP 7: {e}")
            
            try:
                # Data-driven fallback with safe extraction
                location_str = f"{area}, {city}" if area else (city if city else "the area")
                current_price = float(estimated_current_price) if estimated_current_price else 10000000
                forecast_5yr = float(forecast_data.get('predicted_5', current_price * 1.2)) if forecast_data.get('predicted_5') else current_price * 1.2
                inv_score = float(forecast_data.get('score', 0.5)) if forecast_data.get('score') is not None else 0.5
                
                growth_pct = ((forecast_5yr - current_price) / current_price * 100) if current_price > 0 else 20.0
                growth_term = "strong" if growth_pct > 30 else "steady" if growth_pct > 15 else "modest"
                score_term = "attractive" if inv_score > 0.7 else "balanced"
                bhk_val = bhk if bhk else 2
                risk_val = risk if risk else "Moderate"
                
                explanation = (
                    f"The {bhk_val} BHK property in {location_str} priced near Rs {current_price:,.0f} "
                    f"shows {growth_term} long-term potential with an estimated {growth_pct:.1f}% appreciation. "
                    f"The {risk_val.lower()} risk profile is supported by infrastructure and demand patterns, "
                    f"with investment score of {inv_score:.2f} indicating a {score_term} opportunity. "
                    f"While short-term fluctuations may occur, fundamentals suggest stable growth prospects."
                )
            except:
                explanation = (
                    "The property presents balanced long-term investment potential supported by "
                    "local infrastructure and steady demand patterns, with moderate market risks."
                )
        
        # STEP 8: Build Response Summary
        loc_text = f"{area}, {city}" if area else city
        summary = f"{bhk} BHK property in {loc_text}, {size_sqft} sqft. Current estimated price: ₹{estimated_current_price:,.0f}"
        
        print(f"{'='*70}")
        print(f" ANALYSIS COMPLETE")
        print(f"{'='*70}\n")

        return AnalyzeResponse(
            summary=summary,
            forecast=forecast_price,
            risk=risk,
            risk_explanation=risk_explanation,
            estimated_current_price=estimated_current_price,
            base_price=base_price,
            price_per_sqft=price_per_sqft,
            serp_average=serp_average,
            amenity_boost_pct=amenity_boost_pct,
            news_impact_pct=news_impact_pct,
            location={
                "lat": lat,
                "lng": lng,
                "city": city,
                "area": area,
                "data": loc_data
            },
            amenities=amenities,
            news=news_results,
            explanation=explanation,
            forecast_details={
                "amenity_score": forecast_data.get('amenity_score', 0),
                "amenity_count": forecast_data.get('amenity_count', 0),
                "news_score": forecast_data.get('news_score', 0),
                "news_pos": forecast_data.get('news_pos', 0),
                "news_neg": forecast_data.get('news_neg', 0),
                "overall_score": forecast_data.get('score', 0),
                "explanation_path": forecast_data.get('explanation_path'),
                "predicted_5": forecast_data.get('predicted_5')
            },
            methodology=methodology
        )
        
    except Exception as e:
        print(f" Critical error in analyze_property: {e}\n")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


def _compute_risk_assessment(news_results, amenities, forecast_data, city, area):
    """
    Compute professional risk assessment based on:
    - News sentiment (positive vs negative)
    - Amenity density and quality
    - Market volatility indicators
    - Forecast confidence
    
    Returns: (risk_level, risk_explanation)
    """
    
    # Handle error states in news
    if not news_results or (isinstance(news_results[0], dict) and 
                            ("error" in news_results[0] or "note" in news_results[0])):
        return "Unknown", "Risk assessment unavailable due to insufficient news data."
    
    # Extract metrics from forecast data
    news_pos = forecast_data.get('news_pos', 0)
    news_neg = forecast_data.get('news_neg', 0)
    news_score = forecast_data.get('news_score', 0)
    amenity_count = forecast_data.get('amenity_count', 0)
    amenity_score = forecast_data.get('amenity_score', 0)
    overall_score = forecast_data.get('score', 0.5)
    
    # Count valid news items
    valid_news_count = sum(1 for item in news_results 
                           if isinstance(item, dict) and 'error' not in item and 'note' not in item)
    
    # Initialize risk scoring
    risk_points = 0  # Higher = More risk
    risk_factors = []
    positive_factors = []
    
    # FACTOR 1: News Sentiment Analysis
    if news_neg > news_pos * 1.5:  # Significantly more negative news
        risk_points += 3
        risk_factors.append(f"High negative news sentiment ({news_neg} negative vs {news_pos} positive)")
    elif news_pos > news_neg * 2:  # Strongly positive news
        risk_points -= 2
        positive_factors.append(f"Strong positive sentiment ({news_pos} positive developments)")
    elif news_score < -0.3:  # Overall negative sentiment
        risk_points += 2
        risk_factors.append(f"Negative market sentiment (score: {news_score:.2f})")
    elif news_score > 0.3:  # Overall positive sentiment
        risk_points -= 1
        positive_factors.append(f"Positive market outlook (score: {news_score:.2f})")
    
    # FACTOR 2: Amenity Density & Quality
    if amenity_count < 10:
        risk_points += 2
        risk_factors.append(f"Limited amenities ({amenity_count} facilities)")
    elif amenity_count > 30:
        risk_points -= 2
        positive_factors.append(f"Excellent amenity infrastructure ({amenity_count} facilities)")
    
    if amenity_score < 0.3:
        risk_points += 1
        risk_factors.append(f"Low amenity quality score ({amenity_score:.2f})")
    elif amenity_score > 0.7:
        risk_points -= 1
        positive_factors.append(f"High-quality amenity mix (score: {amenity_score:.2f})")
    
    # FACTOR 3: Market Volatility
    if valid_news_count > 8:
        risk_points += 1
        risk_factors.append(f"High market activity ({valid_news_count} recent articles - potential volatility)")
    elif valid_news_count < 2:
        risk_points += 1
        risk_factors.append(f"Limited market information ({valid_news_count} articles)")
    
    # FACTOR 4: Overall Investment Score
    if overall_score < 0.35:
        risk_points += 2
        risk_factors.append(f"Low investment score ({overall_score:.2f}/1.0)")
    elif overall_score > 0.70:
        risk_points -= 2
        positive_factors.append(f"Strong investment metrics ({overall_score:.2f}/1.0)")
    elif overall_score > 0.55:
        risk_points -= 1
        positive_factors.append(f"Good investment potential ({overall_score:.2f}/1.0)")
    
    # FACTOR 5: Infrastructure Development
    # Check if SERP data was available (indicates market liquidity)
    if forecast_data.get('serp_average'):
        risk_points -= 1
        positive_factors.append("Active market with verified listings")
    
    # Determine Risk Level
    if risk_points >= 4:
        risk_level = "High Risk"
    elif risk_points >= 1:
        risk_level = "Medium Risk"
    elif risk_points <= -2:
        risk_level = "Low Risk"
    else:
        risk_level = "Low-Medium Risk"
    
    # Build Explanation
    location_str = f"{area}, {city}" if area else city
    explanation_parts = [f"Risk assessment for {location_str}:"]
    
    if risk_factors:
        explanation_parts.append(f"\n\n Concerns: {' • '.join(risk_factors)}.")
    
    if positive_factors:
        explanation_parts.append(f"\n\n Strengths: {' • '.join(positive_factors)}.")
    
    if not risk_factors and not positive_factors:
        explanation_parts.append("\n\n Balanced market conditions with moderate indicators.")
    
    # Add Recommendation
    explanation_parts.append("\n\n Recommendation: ")
    if risk_level == "High Risk":
        explanation_parts.append("Conduct extensive due diligence. Consider postponing investment until market stabilizes.")
    elif risk_level == "Medium Risk":
        explanation_parts.append("Monitor market developments closely. Seek professional valuation before proceeding.")
    elif "Low-Medium" in risk_level:
        explanation_parts.append("Favorable conditions overall. Standard due diligence recommended.")
    else:  # Low Risk
        explanation_parts.append("Strong investment opportunity. Proceed with standard verification processes.")
    
    risk_explanation = "".join(explanation_parts)
    
    return risk_level, risk_explanation