import os
import requests
from dotenv import load_dotenv
load_dotenv()

SERPAPI_URL = "https://serpapi.com/search"
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"

class NewsService:
    def __init__(self):
        self.serp_key = os.getenv("SERP_API_KEY")
        self.gemini_key = os.getenv("GEMINI_API_KEY")
        if not self.serp_key or not self.gemini_key:
            raise RuntimeError("SERP_API_KEY or GEMINI_API_KEY missing in .env")
        self.session = requests.Session()

    def search_news(self, query: str, num: int = 8):
        params = {"api_key": self.serp_key, "engine": "google", "q": query, "tbm": "nws", "num": num}
        r = self.session.get(SERPAPI_URL, params=params, timeout=20)
        r.raise_for_status()
        items = r.json().get("news_results") or []
        return [{"title": n.get("title"), "snippet": n.get("snippet"), "source": n.get("source"), "link": n.get("link")} for n in items]

    def call_gemini(self, prompt: str):
        payload = {"contents":[{"parts":[{"text": prompt}]}]}
        url = f"{GEMINI_URL}?key={self.gemini_key}"
        r = self.session.post(url, json=payload, timeout=30)
        r.raise_for_status()
        return r.json()
