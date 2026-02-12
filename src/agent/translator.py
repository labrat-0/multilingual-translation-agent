import requests
import torch

import time

RATE_LIMIT = 5  # seconds between requests
def translate_text(text: str, source_language: str, target_language: str) -> str:
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
        print(f"API Exception: {str(e)}")
        return {
            "error": f"Request Exception: {str(e)}"
        }
