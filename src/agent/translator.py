from __future__ import annotations

import logging
from typing import Dict

import requests

API_URL = "https://libretranslate.com/translate"
TIMEOUT_SECONDS = 15
MAX_TEXT_LENGTH = 5000

logger = logging.getLogger(__name__)


def translate_text(text: str, source_language: str, target_language: str, api_key: str | None = None) -> Dict[str, str | int | float]:
    if not api_key:
        return {
            "error": "LibreTranslate now requires an API key. Provide the key via the 'api_key' input field."
        }

    if len(text) > MAX_TEXT_LENGTH:
        return {
            "error": f"Text exceeds the {MAX_TEXT_LENGTH}-character limit."
        }

    headers = {
        "Authorization": f"Bearer {api_key}"
    }
    payload = {
        "q": text,
        "source": source_language,
        "target": target_language,
        "format": "text"
    }

    try:
        response = requests.post(API_URL, data=payload, headers=headers, timeout=TIMEOUT_SECONDS)
        if response.status_code == 200:
            data = response.json()
            translated_text = data.get("translatedText")
            if not translated_text:
                return {"error": "Translation service returned an empty response."}

            from .pricing import calculate_billing

            billing = calculate_billing(text)
            return {
                "original_text": text,
                "translated_text": translated_text,
                "character_count": billing["character_count"],
                "billing_amount": billing["amount"]
            }

        if response.status_code == 400:
            return {
                "error": "LibreTranslate returned 400: check that your API key is valid and your language codes are supported."
            }

        logger.error("LibreTranslate error %s: %s", response.status_code, response.text)
        return {
            "error": f"LibreTranslate error {response.status_code}."
        }

    except requests.exceptions.RequestException as exc:
        logger.exception("LibreTranslate request failed: %s", exc)
        return {
            "error": f"Request failed: {exc}"
        }

