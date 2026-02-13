import asyncio
from apify import Actor
# Import your translation logic
# Make sure the path below matches your file structure exactly!
from .translator import translate_text
import re 

async def main():
    async with Actor:
        # 1. Get the input from the Apify UI
        actor_input = await Actor.get_input() or {}
        text = actor_input.get("text")
        target_lang = actor_input.get("target_language", "fr")

        # Validate inputs
        def is_valid_iso639_1(code):
            return bool(re.fullmatch(r'^[a-z]{2}$', code, re.IGNORECASE))

        if not text:
            print("Error: No text provided in input!")
            return

        if not is_valid_iso639_1(target_lang):
            print(f"Error: Invalid target language code '{target_lang}'. Must be a valid ISO 639-1 code.")
            return

        source_lang = actor_input.get("source_language", "en")
        if source_lang and not is_valid_iso639_1(source_lang):
            print(f"Error: Invalid source language code '{source_lang}'. Must be a valid ISO 639-1 code.")
            return
        if not text:
            print("No text provided in input!")
            return

        print(f"Translating: {text} to {target_lang}")

        # 2. Run your translation logic
        # Note: The first time this runs, it WILL be slow because 
        # it's downloading the model (~300MB) inside the RUNNING actor.
        api_key = actor_input.get("api_key")
        translation = translate_text(text, actor_input.get("source_language", "en"), target_lang, api_key=api_key)

        # 3. PUSH THE DATA (This makes it appear in the 'Results' tab)
        import time
        start_time = time.time()
        await Actor.push_data({
            "original_text": text,
            "translated_text": translation,
            "target_language": target_lang,
            "source_language": source_lang,
            "character_count": len(text),
            "translation_time": time.time() - start_time
        })
        
        print("Done! Check the 'Results' tab.")

if __name__ == "__main__":
    asyncio.run(main())
