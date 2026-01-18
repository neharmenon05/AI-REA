from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from pathlib import Path

from backend.routes.chat import router as chat_router
from backend.routes.forecast import router as forecast_router
from backend.routes.news import router as news_router
from backend.routes.properties import router as properties_router
from backend.routes.analyze import router as analyze_router

# Explicitly load backend/.env so services read keys when uvicorn started from project root
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)

app = FastAPI(title="AI Real Estate Backend")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # <- allows all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat_router, prefix="/chat", tags=["Chat"])
app.include_router(forecast_router, prefix="/forecast", tags=["Forecast"])
app.include_router(news_router, prefix="/news", tags=["News"])
app.include_router(properties_router, prefix="/properties", tags=["Properties"])
app.include_router(analyze_router, prefix="/api/analyze", tags=["Analyze"])


@app.get("/debug/keys")
def debug_keys():
    """Dev helper: shows which API keys are available (only for local debugging)."""
    import os
    keys = {
        "SERP_API_KEY": bool(os.getenv("SERP_API_KEY")),
        "GEMINI_API_KEY": bool(os.getenv("GEMINI_API_KEY")),
        "GOOGLE_PLACES_API_KEY": bool(os.getenv("GOOGLE_PLACES_API_KEY")),
    }
    return {"env_keys_present": keys}

@app.get("/")
def root():
    return {"status": "AI Real Estate Backend is running"}
