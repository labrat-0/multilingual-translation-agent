import asyncio
from apify import Actor
# Import your translation logic
# Make sure the path below matches your file structure exactly!
from .translator import translate_text 

async def main():
    async with Actor:
        # 1. Get the input from the Apify UI
        actor_input = await Actor.get_input() or {}
        text = actor_input.get("text")
        target_lang = actor_input.get("target_language", "fr")

        # Check if text exists to avoid errors
        if not text:
            print("No text provided in input!")
            return

        print(f"Translating: {text} to {target_lang}")

        # 2. Run your translation logic
        # Note: The first time this runs, it WILL be slow because 
        # it's downloading the model (~300MB) inside the RUNNING actor.
        translation = translate_text(text, actor_input.get("source_language", "en"), target_lang)

        # 3. PUSH THE DATA (This makes it appear in the 'Results' tab)
        await Actor.push_data({
            "original_text": text,
            "translated_text": translation,
            "target_language": target_lang
        })
        
        print("Done! Check the 'Results' tab.")

if __name__ == "__main__":
    asyncio.run(main())
