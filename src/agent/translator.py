import requests
import torch

import time

RATE_LIMIT = 5  # seconds between requests
def translate_text(text: str, source_language: str, target_language: str) -> str:
    if len(text) > 5000:
        return "Error: Text exceeds the 5000-character limit."

    time.sleep(RATE_LIMIT)  # Enforce rate limiting
    url = "https://libretranslate.com/translate"
    payload = {
        "q": text,
        "source": source_language,
        "target": target_language,
        "format": "text"
    }
    response = requests.post(url, data=payload)
    if response.status_code == 200:
        translated_text = response.json().get("translatedText", "Translation failed")
    else:
        translated_text = "Error: Unable to translate"
    return translated_text
