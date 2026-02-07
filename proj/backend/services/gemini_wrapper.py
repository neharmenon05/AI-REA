import os
import requests
from typing import Optional, Dict, Any
import time


class GeminiWrapper:
    """
    Gemini 2.5 Flash API wrapper using generateContent (v1beta).
    Returns a natural human-style paragraph explanation.
    Falls back if API fails.
    """

    def __init__(self):
        self.key = os.getenv("GEMINI_API_KEY")
        self.url = os.getenv(
            "GEMINI_URL",
            "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
        )
        self.timeout = 30
        self.max_retries = 2

    def _get_fallback_text(self) -> str:
        """Return the default fallback text."""
        return (
            "Based on the property configuration, surrounding infrastructure, and prevailing market trends, "
            "this asset presents balanced long-term investment potential. The locality benefits from essential amenities "
            "and steady housing demand, supporting gradual value appreciation rather than speculative spikes. "
            "While short-term fluctuations may occur due to broader economic cycles, fundamentals indicate stable growth prospects."
        )

    def _extract_response_text(self, data: Dict[str, Any]) -> Optional[str]:
        """
        Safely extract text from Gemini API response.
        
        Args:
            data: JSON response from API
            
        Returns:
            Extracted text or None if extraction fails
        """
        try:
            candidates = data.get("candidates", [])
            if not candidates:
                print("WARNING: No candidates in response")
                return None

            content = candidates[0].get("content", {})
            parts = content.get("parts", [])
            
            if not parts:
                print("WARNING: No parts in content")
                return None
            
            if "text" not in parts[0]:
                print("WARNING: No text in parts[0]")
                return None
            
            # Extract the raw text
            raw_text = parts[0]["text"]
            
            # Clean up text: remove extra newlines, preserve single spaces
            text = raw_text.strip().replace("\n", " ")
            # Normalize multiple spaces to single space
            text = " ".join(text.split())
            
            return text

        except (KeyError, IndexError, AttributeError, TypeError) as e:
            print(f"WARNING: Error extracting text from response: {e}")
            return None

    def _make_request(self, payload: Dict[str, Any], debug: bool = False) -> Optional[Dict[str, Any]]:
        """
        Make HTTP request to Gemini API with retry logic.
        
        Args:
            payload: Request payload
            debug: Enable debug logging
            
        Returns:
            JSON response or None if all retries fail
        """
        for attempt in range(self.max_retries):
            try:
                if debug and attempt > 0:
                    print(f"RETRY: Attempt {attempt + 1}/{self.max_retries}")

                response = requests.post(
                    f"{self.url}?key={self.key}",
                    headers={"Content-Type": "application/json"},
                    json=payload,
                    timeout=self.timeout,
                )

                if debug:
                    print(f"API Status Code: {response.status_code}")

                # Raise exception for bad status codes
                response.raise_for_status()
                
                json_response = response.json()
                
                if debug:
                    print(f"Response keys: {json_response.keys()}")
                    if 'candidates' in json_response:
                        print(f"Number of candidates: {len(json_response['candidates'])}")
                
                return json_response

            except requests.exceptions.Timeout:
                print(f"TIMEOUT: Request timeout (attempt {attempt + 1}/{self.max_retries})")
                if attempt < self.max_retries - 1:
                    time.sleep(1)  # Brief pause before retry
                    
            except requests.exceptions.HTTPError as e:
                print(f"HTTP ERROR {response.status_code}: {e}")
                if debug and hasattr(response, 'text'):
                    print(f"Response excerpt: {response.text[:500]}")
                # Don't retry on HTTP errors (4xx, 5xx)
                break
                
            except requests.exceptions.RequestException as e:
                print(f"REQUEST ERROR: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(1)
                    
            except Exception as e:
                print(f"UNEXPECTED ERROR: {e}")
                break

        return None

    def generate_explanation(
        self, 
        prompt: str, 
        max_tokens: Optional[int] = None,  # No limit by default
        debug: bool = False
    ) -> str:
        """
        Generate explanation using Gemini API with automatic fallback.
        
        Args:
            prompt: The input prompt for Gemini
            max_tokens: Maximum tokens in response (None = no limit, uses model default)
            debug: Enable debug output (default: False)
            
        Returns:
            Generated explanation text or fallback text if API fails
        """
        # Check credentials
        if not self.key or not self.url:
            if debug:
                print("WARNING: Gemini key or URL missing - using fallback text.")
            return self._get_fallback_text()

        # Optimized system instruction for concise responses
        system_instruction = (
            "You are a professional real estate investment consultant. "
            "Write EXACTLY ONE concise paragraph (4-6 sentences, maximum 150 words). "
            "No bullet points, no numbering, no headings, no labels. "
            "Cover: investment outlook, key growth drivers, and main risks. "
            "Use professional advisory tone. Be direct and comprehensive."
        )

        # Construct payload - conditionally add maxOutputTokens only if specified
        generation_config = {
            "temperature": 0.7,
            "topP": 0.9,
            "topK": 40
        }
        
        # Only set maxOutputTokens if a limit is specified
        if max_tokens is not None:
            generation_config["maxOutputTokens"] = max_tokens

        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": system_instruction + "\n\n" + prompt}]
                }
            ],
            "generationConfig": generation_config,
            "safetySettings": [
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": "BLOCK_NONE"
                },
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH",
                    "threshold": "BLOCK_NONE"
                },
                {
                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "threshold": "BLOCK_NONE"
                },
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "threshold": "BLOCK_NONE"
                }
            ]
        }

        if debug:
            print(f"\n{'='*60}")
            print(f"SENDING REQUEST TO GEMINI")
            print(f"URL: {self.url}")
            print(f"Max Tokens: {max_tokens if max_tokens else 'No Limit (Model Default)'}")
            print(f"{'='*60}")

        # Make API call
        try:
            data = self._make_request(payload, debug)
            
            if not data:
                if debug:
                    print("WARNING: No data returned from API - using fallback")
                return self._get_fallback_text()

            # Check for finish reason
            if debug and 'candidates' in data and len(data['candidates']) > 0:
                finish_reason = data['candidates'][0].get('finishReason', 'UNKNOWN')
                print(f"Finish Reason: {finish_reason}")
                
                if finish_reason == 'SAFETY':
                    print("WARNING: Response blocked by safety filters")
                elif finish_reason == 'MAX_TOKENS':
                    print("INFO: Response completed at max tokens (may be truncated)")
                elif finish_reason == 'STOP':
                    print("INFO: Response completed naturally")

            # Extract text from response
            text = self._extract_response_text(data)
            
            if not text:
                if debug:
                    print("WARNING: Could not extract text from response - using fallback")
                    print(f"Full response: {data}")
                return self._get_fallback_text()

            # Validate text length (very permissive - accept anything > 10 chars)
            if len(text.strip()) < 10:
                if debug:
                    print(f"WARNING: Response too short ({len(text)} chars) - using fallback")
                return self._get_fallback_text()

            if debug:
                print(f"SUCCESS: Generated {len(text)} character response")
                print(f"Full response: {text}")
                print(f"{'='*60}\n")

            return text

        except Exception as e:
            print(f"ERROR in generate_explanation: {e}")
            if debug:
                import traceback
                traceback.print_exc()
            return self._get_fallback_text()