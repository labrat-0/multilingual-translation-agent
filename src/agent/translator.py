from __future__ import annotations

import logging
import os
from typing import Dict

import requests

# Self-hosted endpoint via env var, falls back to public LibreTranslate
DEFAULT_API_URL = "https://libretranslate.com/translate"
API_URL = os.environ.get("LIBRETRANSLATE_URL", DEFAULT_API_URL)
API_KEY = os.environ.get("LIBRETRANSLATE_API_KEY", "")

TIMEOUT_SECONDS = 15

logger = logging.getLogger(__name__)


def translate_text(
    text: str,
    source_language: str,
    target_language: str,
    api_key: str | None = None,
) -> Dict[str, str | int | float]:
    """Translate text via LibreTranslate.

    Auth resolution order:
    1. api_key parameter (user-supplied via actor input)
    2. LIBRETRANSLATE_API_KEY env var (server-side secret for self-hosted)
    3. No key (works if self-hosted instance has no auth)
    """
    resolved_key = api_key or API_KEY

    headers: dict[str, str] = {}
    if resolved_key:
        headers["Authorization"] = f"Bearer {resolved_key}"

    payload = {
        "q": text,
        "source": source_language,
        "target": target_language,
        "format": "text",
    }

    try:
        response = requests.post(
            API_URL, data=payload, headers=headers, timeout=TIMEOUT_SECONDS
        )

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
                "billing_amount": billing["amount"],
            }

        if response.status_code == 400:
            return {
                "error": "LibreTranslate returned 400: check that language codes are supported."
            }

        if response.status_code in (401, 403):
            return {
                "error": "LibreTranslate authentication failed. Check your API key or server configuration."
            }

        logger.error("LibreTranslate error %s: %s", response.status_code, response.text)
        return {"error": f"LibreTranslate error {response.status_code}."}

    except requests.exceptions.RequestException as exc:
        logger.exception("LibreTranslate request failed: %s", exc)
        return {"error": f"Request failed: {exc}"}
