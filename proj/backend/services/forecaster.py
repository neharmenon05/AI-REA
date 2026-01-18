import os
import json
import time
import requests
import torch
import torch.nn as nn
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import TimeSeriesSplit
from backend.services.gemini_wrapper import GeminiWrapper

class TinyLSTMForecaster:
    """
    LSTM-based property price forecaster:
    - Base price from JSON
    - Optional SERP API market data (max 10 listings)
    - Weighted amenity scoring
    - News sentiment analysis
    - Fallback growth model if needed
    """
    
    def __init__(self, device=None):
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.dataset_path = "backend/api/datasets/price_trend.csv"
        self.base_prices_path = "backend/services/base_prices.json"
        self.serp_api_key = os.getenv("SERP_API_KEY", "")
        
    def _load_base_prices(self):
        try:
            with open(self.base_prices_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print("Warning: base_prices.json load failed:", e)
            return {}
    
    def _get_base_price_per_sqft(self, city, area=None, bhk=None):
        """
        Get base price per sqft from base_prices.json (CASE-INSENSITIVE)
        Structure: city → area → BHK → per_sqft_price
        Falls back to city average if area not found
        """
        base_prices = self._load_base_prices()
        
        try:
            # MAKE CASE-INSENSITIVE: Create a mapping of lowercase keys to original keys
            city_mapping = {k.lower(): k for k in base_prices.keys()}
            
            # Normalize input city to lowercase for lookup
            city_lower = city.lower() if city else ""
            
            # Get actual city key from mapping
            actual_city_key = city_mapping.get(city_lower)
            
            if not actual_city_key:
                print(f"⚠️ City '{city}' not found in base_prices.json, using default ₹2000/sqft")
                return 2000.0
            
            city_data = base_prices[actual_city_key]
            
            # If area specified, make area lookup case-insensitive too
            if area:
                area_mapping = {k.lower(): k for k in city_data.keys()}
                area_lower = area.lower()
                actual_area_key = area_mapping.get(area_lower)
                
                if actual_area_key:
                    area_data = city_data[actual_area_key]
                    if bhk and str(bhk) in area_data:
                        price = float(area_data[str(bhk)])
                        print(f"✓ Found exact match: {actual_city_key}/{actual_area_key}/{bhk}BHK = ₹{price}/sqft")
                        return price
                    # Return average across BHKs in this area
                    bhk_prices = [float(v) for v in area_data.values() 
                                if isinstance(v, (int, float)) or (isinstance(v, str) and v.replace('.','').replace('-','').isdigit())]
                    if bhk_prices:
                        avg = sum(bhk_prices) / len(bhk_prices)
                        print(f"✓ Using area average: {actual_city_key}/{actual_area_key} = ₹{avg:.0f}/sqft")
                        return avg
            
            # Fallback: city average for this BHK across all areas
            all_bhk_prices = []
            for area_name, area_data in city_data.items():
                if isinstance(area_data, dict):
                    if bhk and str(bhk) in area_data:
                        val = area_data[str(bhk)]
                        if isinstance(val, (int, float)):
                            all_bhk_prices.append(float(val))
                    else:
                        # Add all valid BHK prices from this area
                        for k, v in area_data.items():
                            if isinstance(v, (int, float)):
                                all_bhk_prices.append(float(v))
            
            if all_bhk_prices:
                avg = sum(all_bhk_prices) / len(all_bhk_prices)
                print(f"✓ Using city average for {actual_city_key}: ₹{avg:.0f}/sqft")
                return avg
            
            # Ultimate fallback
            print(f"⚠️ No data found for {city}, using default ₹2000/sqft")
            return 2000.0
            
        except Exception as e:
            print(f"⚠️ Error in _get_base_price_per_sqft: {e}")
            return 2000.0

    def _fetch_serp_listings(self, city, area, bhk):
        if not self.serp_api_key:
            print("SERP API key not configured, skipping SERP fetch")
            return None
        try:
            location_query = f"{area}, {city}" if area else city
            search_query = f"{bhk} bhk flat for sale in {location_query}"
            print(f"Fetching SERP listings for: {search_query}")

            params = {
                "api_key": self.serp_api_key,
                "engine": "google",
                "q": search_query,
                "location": "India",
                "gl": "in",
                "hl": "en",
                "num": 20
            }
            response = requests.get("https://serpapi.com/search", params=params, timeout=15)
            if response.status_code != 200:
                print(f"SERP API returned status {response.status_code}")
                return None
            data = response.json()
            prices = []
            import re
            for result in data.get("organic_results", []):
                snippet = result.get("snippet", "")
                title = result.get("title", "")
                text = f"{title} {snippet}".lower()
                price_patterns = [
                    r'[₹rs\.]*\s*(\d+\.?\d*)\s*(cr|crore|crores)',
                    r'[₹rs\.]*\s*(\d+\.?\d*)\s*(l|lac|lacs|lakh|lakhs)',
                    r'₹\s*([\d,]+)',
                    r'rs\.?\s*([\d,]+)',
                    r'inr\s*([\d,]+)'
                ]
                for pattern in price_patterns:
                    matches = re.findall(pattern, text, re.IGNORECASE)
                    for match in matches:
                        try:
                            if isinstance(match, tuple) and len(match) >= 2:
                                value_str = match[0].replace(',', '')
                                value = float(value_str)
                                unit = match[1].lower()
                                if 'cr' in unit:
                                    price = value * 10000000
                                elif 'l' in unit:
                                    price = value * 100000
                                else:
                                    price = value
                            else:
                                value_str = str(match[0]).replace(',', '')
                                price = float(value_str)
                            if 500000 <= price <= 1000000000:
                                prices.append(price)
                                break
                        except:
                            continue
            if not prices:
                return None
            prices = sorted(prices)[:10]
            avg_price = sum(prices)/len(prices)
            print(f"Using {len(prices)} SERP listings, average price: {avg_price:.0f}")
            return avg_price
        except Exception as e:
            print("SERP fetch failed:", e)
            return None

    def _load_dataset(self):
        try:
            df = pd.read_csv(self.dataset_path)
            if 'Price' in df.columns:
                series = pd.to_numeric(df['Price'], errors='coerce').dropna().values.astype(np.float32)
                print(f"Loaded {len(series)} historical price points from dataset")
                return series
            print("Price column not found in dataset, using synthetic data")
            return np.linspace(2000000.0, 5000000.0, num=50).astype(np.float32)
        except:
            print("Dataset not found, using synthetic data")
            return np.linspace(2000000.0, 5000000.0, num=50).astype(np.float32)

    def _compute_amenity_score(self, amenities):
        if not amenities or not isinstance(amenities, dict):
            return 0.0, 0
        amenity_count = 0
        schools = 0
        hospitals = 0
        parks = 0
        malls = 0
        for key, value in amenities.items():
            count = 0
            if isinstance(value, dict) and 'places' in value:
                count = len(value['places'])
            elif isinstance(value, list):
                count = len(value)
            elif isinstance(value, (int, float)):
                count = int(value)
            amenity_count += count
            key_lower = key.lower()
            if 'school' in key_lower or 'college' in key_lower or 'university' in key_lower:
                schools += count
            elif 'hospital' in key_lower or 'clinic' in key_lower:
                hospitals += count
            elif 'park' in key_lower or 'garden' in key_lower:
                parks += count
            elif 'mall' in key_lower or 'market' in key_lower:
                malls += count
        score = (
            0.3*min(np.sqrt(schools/10),1.0) +
            0.3*min(np.sqrt(hospitals/5),1.0) +
            0.2*min(np.sqrt(parks/5),1.0) +
            0.2*min(np.sqrt(malls/5),1.0)
        )
        score = min(max(score,0.0),1.0)
        print(f"Amenities: Schools={schools}, Hospitals={hospitals}, Parks={parks}, Malls={malls}")
        print(f"Amenity score: {score:.3f} (total count: {amenity_count})")
        return score, amenity_count

    def _compute_news_score(self, news):
        if not news or not isinstance(news, list):
            return 0.0,0,0
        positive_keywords = ['flyover','metro','airport','highway','development','growth','investment','opening','approved']
        negative_keywords = ['flood','crime','closure','delay','pollution','traffic','unsafe']
        pos_count=0
        neg_count=0
        for item in news:
            text=''
            if isinstance(item, dict):
                text=' '.join([str(item.get(k,'')) for k in ['title','snippet','text','description']]).lower()
            else:
                text=str(item).lower()
            for kw in positive_keywords:
                if kw in text:
                    pos_count+=1
            for kw in negative_keywords:
                if kw in text:
                    neg_count+=1
        total = pos_count + neg_count
        if total==0:
            return 0.0,0,0
        score = (pos_count - neg_count)/total
        score = max(min(score,1.0),-1.0)
        print(f"News sentiment: {pos_count} positive, {neg_count} negative, score: {score:+.3f}")
        return score,pos_count,neg_count

    def _create_lstm_model(self):
        class LSTMModel(nn.Module):
            def __init__(self):
                super().__init__()
                self.lstm = nn.LSTM(1,16,1,batch_first=True)
                self.dropout = nn.Dropout(0.2)
                self.fc = nn.Linear(16,1)
            def forward(self,x):
                out,_ = self.lstm(x)
                out = self.dropout(out[:,-1,:])
                return self.fc(out)
        return LSTMModel().to(self.device)

    def _fallback_growth_model(self, base_price, years_to_forecast):
        growth = 0.06
        predictions={}
        for y in years_to_forecast:
            predictions[y]=float(base_price*((1+growth)**y))
        print(f"Using fallback growth model ({growth*100:.0f}% annual growth)")
        return predictions

    def _train_and_forecast_lstm(self, current_price, years_to_forecast):
        hist_prices = self._load_dataset()
        hist_prices = np.append(hist_prices,current_price)
        if len(hist_prices)<15:
            print("Insufficient historical data, using fallback growth")
            return self._fallback_growth_model(current_price, years_to_forecast)
        scaler = MinMaxScaler()
        scaled = scaler.fit_transform(hist_prices.reshape(-1,1)).flatten()
        seq_len=4
        X=[]
        y=[]
        for i in range(len(scaled)-seq_len):
            X.append(scaled[i:i+seq_len])
            y.append(scaled[i+seq_len])
        X_array=np.array(X)
        y_array=np.array(y)
        if len(X_array)<10:
            print("Insufficient sequences for training, using fallback")
            return self._fallback_growth_model(current_price, years_to_forecast)
        X_t = torch.tensor(X_array.reshape(-1,seq_len,1),dtype=torch.float32).to(self.device)
        y_t = torch.tensor(y_array.reshape(-1,1),dtype=torch.float32).to(self.device)
        model=self._create_lstm_model()
        opt=torch.optim.Adam(model.parameters(),lr=0.01)
        loss_fn = nn.MSELoss()
        prev_loss=float('inf')
        patience=20
        patience_counter=0
        for epoch in range(200):
            model.train()
            pred=model(X_t)
            loss=loss_fn(pred,y_t)
            opt.zero_grad()
            loss.backward()
            opt.step()
            current_loss=loss.item()
            if current_loss<prev_loss-1e-6:
                prev_loss=current_loss
                patience_counter=0
            else:
                patience_counter+=1
            if patience_counter>=patience:
                print(f"Early stopping at epoch {epoch}")
                break
        model.eval()
        last_seq=torch.tensor(scaled[-seq_len:].reshape(1,seq_len,1),dtype=torch.float32).to(self.device)
        preds=[]
        with torch.no_grad():
            seq=last_seq.clone()
            for _ in range(max(years_to_forecast)):
                out=model(seq)
                preds.append(out.cpu().numpy().flatten()[0])
                seq=torch.cat([seq[:,1:,:],out.reshape(1,1,1)],axis=1)
        preds = scaler.inverse_transform(np.array(preds).reshape(-1,1)).flatten()
        for i in range(1,len(preds)):
            if preds[i]<preds[i-1]:
                preds[i]=preds[i-1]*1.02
        preds=np.maximum(preds,current_price)
        predictions={y: float(preds[y-1]) for y in years_to_forecast}
        print(f"LSTM forecast complete: 5yr = {predictions.get(5,current_price):,.0f}")
        return predictions

    def forecast_with_context(self, city, area=None, bhk=None, sqft=None,
                              amenities=None, news=None, query_text=None,
                              years_to_forecast=[2,3,5,10]):
        city = city or "Coimbatore"
        area = area or None
        bhk = bhk or 3
        sqft = sqft or 1000
        price_per_sqft = self._get_base_price_per_sqft(city, area, bhk)
        base_price = price_per_sqft * sqft
        print(f"Base price from JSON: {base_price:.0f} ({price_per_sqft}/sqft × {sqft} sqft)")
        serp_avg = self._fetch_serp_listings(city, area, bhk)
        if serp_avg:
            current_price = (base_price + serp_avg)/2
            print(f"SERP average price: {serp_avg:.0f}, combined current price: {current_price:.0f}")
        else:
            current_price=base_price
            print(f"Current price: {current_price:.0f} (JSON only)")
        amenity_score, amenity_count = self._compute_amenity_score(amenities)
        news_score, news_pos, news_neg = self._compute_news_score(news)
        adjusted_price = current_price*(1+amenity_score*0.1+news_score*0.05)
        print(f"Adjusted price after amenities/news: {adjusted_price:.0f}")
        predictions=self._train_and_forecast_lstm(adjusted_price, years_to_forecast)
        predicted_5 = predictions.get(5,predictions.get(max(years_to_forecast),adjusted_price))
        return {
            'predictions': {str(k): v for k,v in predictions.items()},
            'predicted_5': predicted_5,
            'current_price': adjusted_price,
            'base_price': base_price,
            'serp_average': serp_avg,
            'price_per_sqft': price_per_sqft,
            'amenity_score': amenity_score,
            'amenity_count': amenity_count,
            'news_score': news_score
        }

    def forecast(self, current_price: float, years_to_forecast=[2,5,10]):
        return self._train_and_forecast_lstm(current_price, years_to_forecast)
