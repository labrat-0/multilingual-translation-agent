"""
Multi-provider translation engine.

Supports: LibreTranslate, OpenAI, Anthropic (Claude), Google Gemini.
Each provider returns the same stable dict shape.
"""

from __future__ import annotations

import json
import logging
import os
import time
from typing import Any, Dict

import httpx

from .pricing import calculate_billing
from .validation import sanitize_error

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Default endpoints (hardcoded for SSRF prevention)
# ---------------------------------------------------------------------------

DEFAULT_ENDPOINTS: dict[str, str] = {
    "libretranslate": os.environ.get("LIBRETRANSLATE_URL", "https://libretranslate.com/translate"),
    "openai": "https://api.openai.com/v1/chat/completions",
    "anthropic": "https://api.anthropic.com/v1/messages",
    "gemini": "https://generativelanguage.googleapis.com/v1beta/models",
}

# ---------------------------------------------------------------------------
# Translation system prompt (shared across LLM providers)
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = (
    "You are a professional translator. "
    "Translate the user's text to {target_language}. "
    "Output ONLY the translated text. "
    "Do not add explanations, notes, or quotation marks around the translation. "
    "Preserve the original meaning, tone, and formatting."
)

LANGUAGE_NAMES: dict[str, str] = {
    "en": "English", "es": "Spanish", "fr": "French", "de": "German",
    "it": "Italian", "pt": "Portuguese", "nl": "Dutch", "ru": "Russian",
    "zh": "Chinese", "zh-hans": "Simplified Chinese", "zh-hant": "Traditional Chinese",
    "ja": "Japanese", "ko": "Korean", "ar": "Arabic", "hi": "Hindi",
    "tr": "Turkish", "pl": "Polish", "sv": "Swedish", "da": "Danish",
    "no": "Norwegian", "fi": "Finnish", "cs": "Czech", "el": "Greek",
    "he": "Hebrew", "th": "Thai", "vi": "Vietnamese", "id": "Indonesian",
    "ms": "Malay", "uk": "Ukrainian", "ro": "Romanian", "hu": "Hungarian",
    "bg": "Bulgarian", "hr": "Croatian", "sk": "Slovak", "sl": "Slovenian",
    "lt": "Lithuanian", "lv": "Latvian", "et": "Estonian", "bn": "Bengali",
    "ta": "Tamil", "te": "Telugu", "mr": "Marathi", "ur": "Urdu",
    "fa": "Persian", "sw": "Swahili", "tl": "Filipino", "af": "Afrikaans",
}


def _get_language_name(code: str) -> str:
    """Resolve language code to human-readable name for prompts."""
    return LANGUAGE_NAMES.get(code.lower(), code)


# ---------------------------------------------------------------------------
# Provider implementations
# ---------------------------------------------------------------------------


def _translate_libretranslate(
    text: str,
    source_language: str,
    target_language: str,
    api_key: str | None = None,
    endpoint: str | None = None,
    timeout: int = 30,
    max_retries: int = 3,
    **kwargs: Any,
) -> Dict[str, Any]:
    """Translate via LibreTranslate."""
    url = endpoint or DEFAULT_ENDPOINTS["libretranslate"]
    resolved_key = api_key or os.environ.get("LIBRETRANSLATE_API_KEY", "")

    headers: dict[str, str] = {"Content-Type": "application/x-www-form-urlencoded"}
    if resolved_key:
        headers["Authorization"] = f"Bearer {resolved_key}"

    payload = {
        "q": text,
        "source": source_language,
        "target": target_language,
        "format": "text",
    }

    last_error = ""
    for attempt in range(max_retries):
        try:
            with httpx.Client(timeout=timeout) as client:
                response = client.post(url, data=payload, headers=headers)

            if response.status_code == 200:
                data = response.json()
                translated = data.get("translatedText", "")
                if not translated:
                    return {"error": "LibreTranslate returned an empty response."}

                billing = calculate_billing(text, "libretranslate")
                return {
                    "translated_text": translated,
                    "detected_language": "",
                    "character_count": billing["character_count"],
                    "billing_amount": billing["amount"],
                    "finish_reason": "",
                    "model_used": "",
                }

            if response.status_code == 400:
                return {"error": "LibreTranslate returned 400: check that language codes are supported."}
            if response.status_code in (401, 403):
                return {"error": "LibreTranslate authentication failed. Check your API key."}
            if response.status_code == 429:
                wait = min(2 ** attempt, 10)
                logger.warning("LibreTranslate rate limited, retrying in %ss...", wait)
                time.sleep(wait)
                last_error = f"LibreTranslate rate limited (429) after {max_retries} attempts."
                continue

            last_error = f"LibreTranslate error {response.status_code}."
            logger.error("LibreTranslate error %s: %s", response.status_code, response.text[:200])

        except httpx.HTTPError as exc:
            last_error = sanitize_error(f"LibreTranslate request failed: {exc}", api_key)
            logger.exception("LibreTranslate request failed")
            if attempt < max_retries - 1:
                time.sleep(min(2 ** attempt, 10))

    return {"error": last_error}


def _translate_openai(
    text: str,
    source_language: str,
    target_language: str,
    api_key: str | None = None,
    model: str = "gpt-4o-mini",
    endpoint: str | None = None,
    temperature: float = 0,
    timeout: int = 30,
    max_retries: int = 3,
    **kwargs: Any,
) -> Dict[str, Any]:
    """Translate via OpenAI Chat Completions API."""
    url = endpoint or DEFAULT_ENDPOINTS["openai"]
    target_name = _get_language_name(target_language)

    system_msg = SYSTEM_PROMPT.format(target_language=target_name)
    if source_language and source_language != "auto":
        source_name = _get_language_name(source_language)
        system_msg += f" The source language is {source_name}."

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": text},
        ],
        "temperature": temperature,
    }

    last_error = ""
    for attempt in range(max_retries):
        try:
            with httpx.Client(timeout=timeout) as client:
                response = client.post(url, json=payload, headers=headers)

            if response.status_code == 200:
                data = response.json()
                choice = data.get("choices", [{}])[0]
                translated = choice.get("message", {}).get("content", "").strip()
                finish_reason = choice.get("finish_reason", "")

                if not translated:
                    return {"error": "OpenAI returned an empty translation."}

                billing = calculate_billing(text, "openai")
                return {
                    "translated_text": translated,
                    "detected_language": "",
                    "character_count": billing["character_count"],
                    "billing_amount": billing["amount"],
                    "finish_reason": finish_reason,
                    "model_used": model,
                }

            if response.status_code == 401:
                return {"error": sanitize_error("OpenAI authentication failed. Check your API key.", api_key)}
            if response.status_code == 429:
                wait = min(2 ** attempt, 10)
                logger.warning("OpenAI rate limited, retrying in %ss...", wait)
                time.sleep(wait)
                last_error = f"OpenAI rate limited (429) after {max_retries} attempts."
                continue
            if response.status_code >= 500:
                wait = min(2 ** attempt, 10)
                logger.warning("OpenAI server error %s, retrying...", response.status_code)
                time.sleep(wait)
                last_error = f"OpenAI server error {response.status_code}."
                continue

            last_error = sanitize_error(f"OpenAI error {response.status_code}: {response.text[:200]}", api_key)

        except httpx.HTTPError as exc:
            last_error = sanitize_error(f"OpenAI request failed: {exc}", api_key)
            logger.exception("OpenAI request failed")
            if attempt < max_retries - 1:
                time.sleep(min(2 ** attempt, 10))

    return {"error": last_error}


def _translate_anthropic(
    text: str,
    source_language: str,
    target_language: str,
    api_key: str | None = None,
    model: str = "claude-3-5-haiku-latest",
    endpoint: str | None = None,
    temperature: float = 0,
    timeout: int = 30,
    max_retries: int = 3,
    **kwargs: Any,
) -> Dict[str, Any]:
    """Translate via Anthropic Messages API."""
    url = endpoint or DEFAULT_ENDPOINTS["anthropic"]
    target_name = _get_language_name(target_language)

    system_msg = SYSTEM_PROMPT.format(target_language=target_name)
    if source_language and source_language != "auto":
        source_name = _get_language_name(source_language)
        system_msg += f" The source language is {source_name}."

    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "Content-Type": "application/json",
    }

    payload = {
        "model": model,
        "max_tokens": 4096,
        "system": system_msg,
        "messages": [
            {"role": "user", "content": text},
        ],
        "temperature": temperature,
    }

    last_error = ""
    for attempt in range(max_retries):
        try:
            with httpx.Client(timeout=timeout) as client:
                response = client.post(url, json=payload, headers=headers)

            if response.status_code == 200:
                data = response.json()
                content_blocks = data.get("content", [])
                translated = ""
                for block in content_blocks:
                    if block.get("type") == "text":
                        translated += block.get("text", "")
                translated = translated.strip()
                finish_reason = data.get("stop_reason", "")

                if not translated:
                    return {"error": "Anthropic returned an empty translation."}

                billing = calculate_billing(text, "anthropic")
                return {
                    "translated_text": translated,
                    "detected_language": "",
                    "character_count": billing["character_count"],
                    "billing_amount": billing["amount"],
                    "finish_reason": finish_reason,
                    "model_used": model,
                }

            if response.status_code == 401:
                return {"error": sanitize_error("Anthropic authentication failed. Check your API key.", api_key)}
            if response.status_code == 429:
                wait = min(2 ** attempt, 10)
                logger.warning("Anthropic rate limited, retrying in %ss...", wait)
                time.sleep(wait)
                last_error = f"Anthropic rate limited (429) after {max_retries} attempts."
                continue
            if response.status_code >= 500:
                wait = min(2 ** attempt, 10)
                logger.warning("Anthropic server error %s, retrying...", response.status_code)
                time.sleep(wait)
                last_error = f"Anthropic server error {response.status_code}."
                continue

            last_error = sanitize_error(f"Anthropic error {response.status_code}: {response.text[:200]}", api_key)

        except httpx.HTTPError as exc:
            last_error = sanitize_error(f"Anthropic request failed: {exc}", api_key)
            logger.exception("Anthropic request failed")
            if attempt < max_retries - 1:
                time.sleep(min(2 ** attempt, 10))

    return {"error": last_error}


def _translate_gemini(
    text: str,
    source_language: str,
    target_language: str,
    api_key: str | None = None,
    model: str = "gemini-2.0-flash",
    endpoint: str | None = None,
    temperature: float = 0,
    timeout: int = 30,
    max_retries: int = 3,
    **kwargs: Any,
) -> Dict[str, Any]:
    """Translate via Google Gemini generateContent API."""
    base_url = endpoint or DEFAULT_ENDPOINTS["gemini"]
    url = f"{base_url}/{model}:generateContent?key={api_key}"

    target_name = _get_language_name(target_language)
    prompt = SYSTEM_PROMPT.format(target_language=target_name)
    if source_language and source_language != "auto":
        source_name = _get_language_name(source_language)
        prompt += f" The source language is {source_name}."
    prompt += f"\n\nText to translate:\n{text}"

    headers = {"Content-Type": "application/json"}

    payload = {
        "contents": [
            {"parts": [{"text": prompt}]},
        ],
        "generationConfig": {
            "temperature": temperature,
        },
    }

    last_error = ""
    for attempt in range(max_retries):
        try:
            with httpx.Client(timeout=timeout) as client:
                response = client.post(url, json=payload, headers=headers)

            if response.status_code == 200:
                data = response.json()
                candidates = data.get("candidates", [])
                translated = ""
                finish_reason = ""
                if candidates:
                    parts = candidates[0].get("content", {}).get("parts", [])
                    for part in parts:
                        translated += part.get("text", "")
                    finish_reason = candidates[0].get("finishReason", "")
                translated = translated.strip()

                if not translated:
                    return {"error": "Gemini returned an empty translation."}

                billing = calculate_billing(text, "gemini")
                return {
                    "translated_text": translated,
                    "detected_language": "",
                    "character_count": billing["character_count"],
                    "billing_amount": billing["amount"],
                    "finish_reason": finish_reason,
                    "model_used": model,
                }

            if response.status_code == 400:
                return {"error": sanitize_error(f"Gemini returned 400: {response.text[:200]}", api_key)}
            if response.status_code == 401 or response.status_code == 403:
                return {"error": sanitize_error("Gemini authentication failed. Check your API key.", api_key)}
            if response.status_code == 429:
                wait = min(2 ** attempt, 10)
                logger.warning("Gemini rate limited, retrying in %ss...", wait)
                time.sleep(wait)
                last_error = f"Gemini rate limited (429) after {max_retries} attempts."
                continue
            if response.status_code >= 500:
                wait = min(2 ** attempt, 10)
                logger.warning("Gemini server error %s, retrying...", response.status_code)
                time.sleep(wait)
                last_error = f"Gemini server error {response.status_code}."
                continue

            last_error = sanitize_error(f"Gemini error {response.status_code}: {response.text[:200]}", api_key)

        except httpx.HTTPError as exc:
            last_error = sanitize_error(f"Gemini request failed: {exc}", api_key)
            logger.exception("Gemini request failed")
            if attempt < max_retries - 1:
                time.sleep(min(2 ** attempt, 10))

    return {"error": last_error}


# ---------------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------------

PROVIDER_FUNCTIONS = {
    "libretranslate": _translate_libretranslate,
    "openai": _translate_openai,
    "anthropic": _translate_anthropic,
    "gemini": _translate_gemini,
}


def translate_text(
    text: str,
    source_language: str,
    target_language: str,
    provider: str = "libretranslate",
    api_key: str | None = None,
    model: str | None = None,
    endpoint: str | None = None,
    temperature: float = 0,
    timeout: int = 30,
    max_retries: int = 3,
) -> Dict[str, Any]:
    """Route translation to the selected provider."""
    fn = PROVIDER_FUNCTIONS.get(provider)
    if not fn:
        return {"error": f"Unknown provider: {provider}"}

    kwargs: dict[str, Any] = {
        "text": text,
        "source_language": source_language,
        "target_language": target_language,
        "api_key": api_key,
        "timeout": timeout,
        "max_retries": max_retries,
    }

    if provider != "libretranslate":
        kwargs["model"] = model or ""
        kwargs["temperature"] = temperature

    if endpoint:
        kwargs["endpoint"] = endpoint

    return fn(**kwargs)
