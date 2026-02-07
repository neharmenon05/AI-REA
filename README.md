# Intelligent Real Estate Price Prediction (AI-REA)

This repository was created as part of a Software Engineering project. It demonstrates how natural language processing, geospatial intelligence, market data analysis, and deep learning models
can be combined to build an intelligent assistant for analyzing and forecasting residential real estate properties.
We also have a marketplace from where user can list,search and find the most suitable property for them.Additonaly a agent is designed to simplify task like filling forms,fetching info and description,It also 
simpliefies communication by providing real chat interface.The application is designed to be multilingual and has voice based input support
The system emphasizes explainable analytics, modular architecture, and long-term price forecasting.

---

## Key Features

* Natural language property query processing
* Location and environment intelligence (amenities, livability, infrastructure)
* Market and price intelligence with LSTM-based forecasting
* News-driven qualitative market analysis
* Investment metrics including rental yield, ROI, and risk classification
* Interactive web dashboards and conversational interface
* Agents for easy communication and use
* Multilingual and voice support
* Modular and extensible system design

---

## Folder Structure

```
AI-REA/
│
├── proj/
│   ├── frontend/        # Web frontend application
│   ├── backend/         # Backend APIs and AI/ML processing logic
│   └── reports/         # Literature review and project documentation
│
├── requirements.txt     # Python dependencies
├── .gitignore
└── README.md
```

---

## Setup Guide

### 1. Create and Activate Virtual Environment

```bash
cd AI-REA/proj/backend
python -m venv venv
source venv/bin/activate        # macOS/Linux
venv\Scripts\activate           # Windows
```

---

### 2. Install Backend Dependencies

```bash
pip install -r requirements.txt
```

---

## Environment Configuration

Create a `.env` file inside the `backend/` directory and add the following configuration values:

```
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

**Notes:**

* API keys must be obtained from their respective providers.
* The `.env` file should not be committed to version control.
* All external API calls are routed through the backend layer.

---

## Run the Application

### Backend

```bash
uvicorn backend.main:app --reload
```

---

### Frontend

```bash
cd ../frontend
npm install
npm run dev
```

---

### Access URLs

* Frontend UI: `http://127.0.0.1:5173/`
* Backend API Root: `http://127.0.0.1:8000/`
* Swagger UI: `http://127.0.0.1:8000/docs`
* ReDoc: `http://127.0.0.1:8000/redoc`

---

## Dataset Format

The system operates using file-based datasets and external APIs. Typical dataset (base_price.json) fields include:

```
{
  "Coimbatore": {
    "Gandhipuram": { "1": 2200, "2": 2500, "3": 2800 },
    "Race Course": { "1": 2500, "2": 2800, "3": 3200 },
    "Peelamedu": { "1": 2000, "2": 2300, "3": 2600 },
  }
}

```
In Supabase :
```
  create table public.properties (
    id uuid not null default gen_random_uuid (),
    title text not null,
    description text null,
    location text not null,
    sublocality text not null,
    property_type text not null,
    bhk text not null,
    size numeric not null,
    price numeric not null,
    price_per_sqft numeric null,
    furnishing_status text null,
    parking integer null default 0,
    owner_name text not null,
    owner_email text not null,
    owner_phone text not null,
    images text[] null default array[]::text[],
    status text null default 'active'::text,
    created_at timestamp with time zone null default now(),
    updated_at timestamp with time zone null default now(),
    floor integer null,
    total_floors integer null,
    property_age integer null,
    constraint properties_pkey primary key (id)
  ) TABLESPACE pg_default;
  
  create index IF not exists idx_properties_location on public.properties using btree (location) TABLESPACE pg_default;
  
  create index IF not exists idx_properties_price on public.properties using btree (price) TABLESPACE pg_default;
  
  create index IF not exists idx_properties_bhk on public.properties using btree (bhk) TABLESPACE pg_default;
  
  create index IF not exists idx_properties_type on public.properties using btree (property_type) TABLESPACE pg_default;
  
  create index IF not exists idx_properties_status on public.properties using btree (status) TABLESPACE pg_default;
  
  create trigger trg_price_sqft BEFORE INSERT
  or
  update on properties for EACH row
  execute FUNCTION calc_price_per_sqft ();
  
  create trigger update_properties_updated_at BEFORE
  update on properties for EACH row
  execute FUNCTION update_updated_at_column ();

```
---

## Tech Stack

| Component                             | Description                              |
| ------------------------------------- | ---------------------------------------- |
| Python 3.x                            | Backend development and AI/ML processing |
| FastAPI                               | REST API and backend framework           |
| TensorFlow / Keras                    | LSTM-based deep learning forecasting     |
| scikit-learn                          | Feature preprocessing and evaluation     |
| Pandas / NumPy                        | Data manipulation and analysis           |
| Langraph                              | Agentic Components                       |
| JavaScript Framework (React/Vite/Vue) | Frontend UI and dashboards               |
| External APIs                         | Geocoding, amenities, market news        |

---

## Notes

* Forecasts are probabilistic and include uncertainty bounds.
* No guarantee of prediction accuracy is implied.
* The system does not use a database; all persistence is file-based or in-memory.
* Designed for academic evaluation and extensibility.

---

## Credits

* Software Engineering Project Team
* Open-source Python, AI, and Web Development communities
