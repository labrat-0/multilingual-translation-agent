import asyncio
import re
import time
from typing import Any, Dict

from apify import Actor

from .translator import translate_text

ISO_CODE_PATTERN = re.compile(r"^[a-z]{2}(-[a-zA-Z]{2,4})?$")
MAX_TEXT_LENGTH = 5000


def is_valid_lang_code(code: str | None) -> bool:
    """Validate ISO 639-1 code, with optional subtag (e.g., zh-Hans, pt-BR)."""
    if not code:
        return False
    return bool(ISO_CODE_PATTERN.fullmatch(code))


def normalize_code(code: str) -> str:
    return code.lower()


async def main() -> None:
    async with Actor:
        actor_input: Dict[str, Any] = await Actor.get_input() or {}
        text = actor_input.get("text", "")
        target_lang = normalize_code(actor_input.get("target_language", "fr"))
        source_lang = (
            normalize_code(actor_input.get("source_language", "en"))
            if actor_input.get("source_language")
            else "auto"
        )

        if not text:
            await Actor.fail("No text provided in input.")
            return

        if len(text) > MAX_TEXT_LENGTH:
            await Actor.fail(
                f"Text exceeds maximum length of {MAX_TEXT_LENGTH} characters."
            )
            return

        if not is_valid_lang_code(target_lang):
            await Actor.fail(
                f"Invalid target language code '{target_lang}'. Must be ISO 639-1 (e.g., 'es', 'zh-hans')."
            )
            return

        if source_lang != "auto" and not is_valid_lang_code(source_lang):
            await Actor.fail(
                f"Invalid source language code '{source_lang}'. Must be ISO 639-1 (e.g., 'en', 'pt-br')."
            )
            return

        # api_key from input is optional -- translator.py falls back to env var
        api_key = actor_input.get("api_key")

        start_time = time.time()
        translation = translate_text(text, source_lang, target_lang, api_key=api_key)
        duration = time.time() - start_time

        if translation.get("error"):
            await Actor.fail(translation["error"])
            return

        await Actor.push_data(
            {
                "original_text": text,
                "translated_text": translation["translated_text"],
                "target_language": target_lang,
                "source_language": source_lang,
                "character_count": translation["character_count"],
                "billing_amount": translation["billing_amount"],
                "translation_time": round(duration, 3),
            }
        )

        print("Done! Check the 'Results' tab.")


if __name__ == "__main__":
    asyncio.run(main())
