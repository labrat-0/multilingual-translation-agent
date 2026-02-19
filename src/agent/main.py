"""
Multilingual Translation Agent -- Apify Actor entry point.

Routes translation requests to the selected provider (LibreTranslate, OpenAI,
Anthropic, Google Gemini) and outputs a stable JSON schema.
"""

import asyncio
import logging
import time
from typing import Any, Dict

from apify import Actor

from .translator import translate_text
from .validation import (
    validate_api_key,
    validate_endpoint,
    validate_language_code,
    validate_model,
    validate_provider,
    validate_text,
    sanitize_text,
    DEFAULT_MODELS,
)

logger = logging.getLogger(__name__)


async def main() -> None:
    async with Actor:
        actor_input: Dict[str, Any] = await Actor.get_input() or {}

        # -----------------------------------------------------------------
        # Parse inputs
        # -----------------------------------------------------------------
        test_mode = actor_input.get("testMode", True)
        text_raw = actor_input.get("text", "")
        target_language = actor_input.get("target_language", "es").lower().strip()
        source_language_raw = actor_input.get("source_language")
        source_language = source_language_raw.lower().strip() if source_language_raw else "auto"

        provider = actor_input.get("provider", "libretranslate").lower().strip()
        api_key = actor_input.get("api_key")
        model = actor_input.get("model")
        endpoint = actor_input.get("endpoint")
        temperature = actor_input.get("temperature", 0)
        max_retries = actor_input.get("maxRetries", 3)
        timeout_secs = actor_input.get("timeoutSecs", 30)

        # -----------------------------------------------------------------
        # Test mode -- return mock response for Apify automated QA
        # -----------------------------------------------------------------
        if test_mode:
            logger.warning(
                "Test mode enabled - returning mock response. "
                "Disable test mode and provide an API key to perform real translations."
            )
            text = sanitize_text(text_raw) if text_raw else "How are you today?"
            mock_output = {
                "schema_version": "1.0",
                "provider": "test-mode",
                "model": "test-mode",
                "source_language": source_language,
                "target_language": target_language,
                "detected_language": "",
                "original_text": text,
                "translated_text": "[TEST MODE] No translation performed - this is a mock response",
                "character_count": 0,
                "billing_amount": 0.0,
                "finish_reason": "test-mode",
                "processing_time": 0.0,
            }
            await Actor.push_data(mock_output)
            return

        # -----------------------------------------------------------------
        # Validate inputs
        # -----------------------------------------------------------------

        # Provider
        provider_err = validate_provider(provider)
        if provider_err:
            await Actor.fail(status_message=provider_err)
            return

        # Text
        text = sanitize_text(text_raw)
        text_err = validate_text(text, provider=provider, endpoint=endpoint)
        if text_err:
            await Actor.fail(status_message=text_err)
            return

        # Language codes
        if not validate_language_code(target_language):
            await Actor.fail(
                status_message=f"Invalid target language code '{target_language}'. "
                "Must be ISO 639-1 (e.g., 'es', 'fr', 'zh-hans')."
            )
            return

        if source_language != "auto" and not validate_language_code(source_language):
            await Actor.fail(
                status_message=f"Invalid source language code '{source_language}'. "
                "Must be ISO 639-1 (e.g., 'en', 'pt-br')."
            )
            return

        # API key
        key_err = validate_api_key(provider, api_key)
        if key_err:
            await Actor.fail(status_message=key_err)
            return

        # Model
        resolved_model, model_err = validate_model(provider, model)
        if model_err:
            await Actor.fail(status_message=model_err)
            return

        # Endpoint
        endpoint_err = validate_endpoint(provider, endpoint)
        if endpoint_err:
            await Actor.fail(status_message=endpoint_err)
            return

        # -----------------------------------------------------------------
        # Translate
        # -----------------------------------------------------------------
        logger.info(
            "Translating %d chars with provider=%s model=%s",
            len(text), provider, resolved_model or "(n/a)",
        )

        start_time = time.time()
        result = translate_text(
            text=text,
            source_language=source_language,
            target_language=target_language,
            provider=provider,
            api_key=api_key,
            model=resolved_model,
            endpoint=endpoint,
            temperature=temperature,
            timeout=timeout_secs,
            max_retries=max_retries,
        )
        processing_time = round(time.time() - start_time, 3)

        # -----------------------------------------------------------------
        # Handle error
        # -----------------------------------------------------------------
        if result.get("error"):
            await Actor.fail(status_message=result["error"])
            return

        # -----------------------------------------------------------------
        # Push stable output -- no missing keys
        # -----------------------------------------------------------------
        output = {
            "schema_version": "1.0",
            "provider": provider,
            "model": result.get("model_used", ""),
            "source_language": source_language,
            "target_language": target_language,
            "detected_language": result.get("detected_language", ""),
            "original_text": text,
            "translated_text": result.get("translated_text", ""),
            "character_count": result.get("character_count", 0),
            "billing_amount": result.get("billing_amount", 0.0),
            "finish_reason": result.get("finish_reason", ""),
            "processing_time": processing_time,
        }

        await Actor.push_data(output)
        logger.info("Translation complete in %.3fs", processing_time)


if __name__ == "__main__":
    asyncio.run(main())
