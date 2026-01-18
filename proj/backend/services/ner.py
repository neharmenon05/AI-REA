import re

class SimpleNER:
    """Extract location, bhk, and size from user text."""

    BHK_PATTERNS = [r'(\d+)\s*bhk', r'(\d+)\s*BHK', r'(\d+)\s*bedroom', r'(\d+)\s*br']
    SIZE_PATTERNS = [r'(\d+(?:\.\d+)?)\s*(sq\s*ft|sqft|sqm|square\s*feet|sft|sf|square\s*meter)']
    LOCATION_PATTERNS = [r'in\s+([^,]+)$', r'at\s+([^,]+)$', r'near\s+([^,]+)$']

    def extract(self, text: str) -> dict:
        out = {"location": None, "bhk": None, "size_sqft": None, "raw_text": text}
        s = text.strip()

        # BHK
        for p in self.BHK_PATTERNS:
            m = re.search(p, s, re.I)
            if m: out["bhk"] = int(m.group(1)); break

        # Size
        for p in self.SIZE_PATTERNS:
            m = re.search(p, s, re.I)
            if m:
                val = float(m.group(1))
                if "sqm" in m.group(2).lower() or "meter" in m.group(2).lower():
                    val *= 10.7639
                out["size_sqft"] = val
                break

        # Location
        for p in self.LOCATION_PATTERNS:
            m = re.search(p, s, re.I)
            if m: out["location"] = m.group(1).strip(); break

        if not out["location"]:
            parts = [p.strip() for p in s.split(",") if p.strip()]
            if parts: out["location"] = parts[-1]

        return out
