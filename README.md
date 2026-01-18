# Intelligent Real Estate Price Prediction (AI-REA)

This repository was created as part of a Software Engineering project.It demonstrates how natural language processing, geospatial intelligence, market data analysis, and deep learning models 
can be combined to build an intelligent assistant for analyzing and forecasting residential real estate properties in India.

---
## Key Features

* **Natural Language Query Processing** :
  Accepts free-form property queries and extracts structured information such as location, BHK, size, and user intent.

* **Location & Environment Intelligence**:
  Amenity analysis, livability index computation, and infrastructure readiness classification.

* **Market & Price Intelligence** :
  Current price estimation with confidence ranges and long-term forecasting using LSTM-based deep learning models.

* **News & Qualitative Analysis**
  Integration of location-specific real estate news with contextual impact assessment.

* **Investment Analysis**
  Rental yield estimation, ROI projections, and multi-factor risk classification.

* **Web Application Interface**
  Interactive dashboards, maps, charts, and a conversational chat interface.

* **Modular & Extensible Design**
  Clear separation of frontend, backend, AI/ML logic, and data integration components.

---
## Folder Structure

```
AI-REA/
│
├── proj/
│   ├── frontend/        # Web frontend application
│   ├── backend/         # Backend APIs and AI/ML processing logic
├── requirements.txt     # Python dependencies
├── .gitignore
└── README.md
```

---
##  Setup Guide

### 1. Create and Activate Virtual Environment

```bash
cd AI-REA/proj/backend
python -m venv venv
venv\Scripts\activate           # Windows
source venv/bin/activate        # macOS/Linux
```

### 2. Install Backend and Frontend Dependencies

Run below command in both sub directory 

```bash
pip install -r requirements.txt
```

### 3. Environment Configuration

Create a .env file inside the directory and add the following configuration values:

* **backend/**

``` bash
# API Keys
SERP_API_KEY=
GEMINI_API_KEY=
GOOGLE_PLACES_API_KEY=

# API URLs
SERPAPI_URL=https://serpapi.com/search
GEMINI_URL=https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent
GOOGLE_GEOCODE_URL=https://maps.googleapis.com/maps/api/geocode/json
GOOGLE_PLACES_NEARBY_URL=https://maps.googleapis.com/maps/api/place/nearbysearch/json
GOOGLE_PLACES_DETAILS_URL=https://maps.googleapis.com/maps/api/place/details/json
```

* **frontend/**
``` bash
VITE_SUPABASE_URL= 
VITE_SUPABASE_ANON_KEY=
```

Note: API keys must be obtained from their respective providers.

### 4. Run the Backend Application

```bash
uvicorn backend.main:app --reload
```

### 5. Run the Frontend Application

```bash
cd ../frontend
npm install
npm run dev
```

### 6. Access the Application

* Frontend UI: `http://127.0.0.1:5173/`
* Backend API Root: `http://127.0.0.1:8000/`
---
## Tech Stack

| Component                             | Description                              |
| ------------------------------------- | ---------------------------------------- |
| Python 3.x                            | Backend development and AI/ML processing |
| FastAPI                               | Backend web framework and REST API layer |
| TensorFlow / Keras                    | Deep learning (LSTM) price forecasting   |
| scikit-learn                          | Feature preprocessing and evaluation     |
| Pandas / NumPy                        | Data manipulation and analysis           |
| JavaScript Framework (React/Vite/Vue) | Frontend UI and dashboards               |
| External APIs                         | Geocoding, amenities, and news data      |

---
## Notes

* Forecasts are probabilistic and include clearly stated uncertainty.
* The system does not guarantee price accuracy.
* All persistence is handled through files or runtime context.
* Designed for academic evaluation and future extensibility.




