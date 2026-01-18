import os
import requests

class GeminiWrapper:
    """Simple wrapper to call Google's Generative Language API (Gemini).

    Falls back to a local template when the API key is not configured.
    """
    def __init__(self):
        self.key = os.getenv("GEMINI_API_KEY")
        self.url = os.getenv("GEMINI_URL")

    def generate_explanation(self, prompt: str, max_tokens: int = 200):
        if not self.key or not self.url:
            # fallback: return a canned short explanation
            return (
                "Explanation: using internal heuristics — estimated from BHK and size, "
                "adjusted for amenities and recent news. Exact generative explanation not available (GEMINI_API_KEY missing)."
            )

        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        try:
            resp = requests.post(f"{self.url}?key={self.key}", json=payload, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            # navigate response for text (best-effort)
            choices = data.get("candidates") or data.get("outputs") or []
            if isinstance(choices, list) and choices:
                # try to extract text
                first = choices[0]
                if isinstance(first, dict):
                    # common shape: {'content': '...'} or nested
                    text = first.get("content") or first.get("text") or first.get("output")
                    if isinstance(text, str):
                        return text
                return str(first)
            return str(data)
        except Exception:
            return "Explanation generation failed — using fallback heuristics."
