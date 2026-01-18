from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from backend.services.forecaster import TinyLSTMForecaster

router = APIRouter()

class ForecastRequest(BaseModel):
    current_price: float
    years: Optional[list[int]] = [2, 3, 5, 10]

class ForecastResponse(BaseModel):
    forecasts: dict
    methodology: str
    note: Optional[str] = None

@router.post("/", response_model=ForecastResponse)
def forecast_price(req: ForecastRequest):
    """
    Simple price forecasting endpoint
    
    Input: Current price + forecast horizons
    Output: LSTM-based predictions for specified years
    
    Note: For comprehensive analysis with amenities and news,
    use the /analyze endpoint instead.
    """
    
    try:
        print(f"\n{'='*60}")
        print(f"📈 FORECAST REQUEST")
        print(f"{'='*60}")
        print(f"Current price: ₹{req.current_price:,.0f}")
        print(f"Forecast years: {req.years}\n")
        
        # Validate input
        if req.current_price <= 0:
            raise HTTPException(status_code=400, detail="Current price must be positive")
        
        if not req.years or len(req.years) == 0:
            raise HTTPException(status_code=400, detail="At least one forecast year required")
        
        if any(y <= 0 or y > 30 for y in req.years):
            raise HTTPException(status_code=400, detail="Forecast years must be between 1 and 30")
        
        # Run forecaster
        forecaster = TinyLSTMForecaster()
        result = forecaster.forecast(req.current_price, years_to_forecast=req.years)
        
        print(f"✅ Forecast complete")
        print(f"{'='*60}\n")
        
        return ForecastResponse(
            forecasts=result,
            methodology="LSTM-based time series forecasting",
            note="This is a simple price forecast. For comprehensive analysis with location factors, use /analyze endpoint."
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Forecast error: {e}\n")
        raise HTTPException(status_code=500, detail=f"Forecasting failed: {str(e)}")