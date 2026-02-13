import requests
import torch

import time
from functools import lru_cache

RATE_LIMIT = 5  # seconds between requests
@lru_cache(maxsize=128)
def translate_text(text: str, source_language: str, target_language: str) -> dict | str:
    if len(text) > 5000:
        return {
            "error": "Text exceeds the 5000-character limit."
        }

    time.sleep(RATE_LIMIT)  # Enforce rate limiting
    url = "https://libretranslate.com/translate"
    payload = {
        "q": text,
        "source": source_language,
        "target": target_language,
        "format": "text"
    }
    try:
        response = requests.post(url, data=payload, timeout=10)
        print(f"API Request: {payload}")
        print(f"API Response: {response.status_code}, {response.text}")
        if response.status_code == 200:
            print("Debug: API response headers:", response.headers)
            print("Debug: API response body:", response.text)
            translated_text = response.json().get("translatedText", "Translation failed")
            character_count = len(text)
            from .pricing import calculate_billing
            billing = calculate_billing(text)
            return {
                "original_text": text,
                "translated_text": translated_text,
                "character_count": billing["character_count"],
                "billing_amount": billing["amount"]
            }
        else:
            return {
                "error": f"API Error: {response.status_code} - {response.text}"
            }
    except requests.exceptions.RequestException as e:
        print(f"API Exception: {str(e)}. This may be due to network issues or an invalid API endpoint.")
        return {
            "error": f"Request Exception: {str(e)}"
        }

if __name__ == "__main__":
    # Simulate the error with the failing input
    test_text = "How are you today my friend?"
    source_lang = "en"
    target_lang = "es"
    result = translate_text(test_text, source_lang, target_lang)
    print("Test Result:", result)