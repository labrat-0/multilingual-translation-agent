from apify import Actor
from .translator import translate_text

async def main():
    async with Actor:
        # 1. Get Input
        actor_input = await Actor.get_input() or {}
        text = actor_input.get("text")
        src = actor_input.get("source_language", "en")
        tgt = actor_input.get("target_language", "fr")

        if not text:
            await Actor.fail(status_message="No text provided!")
            return

        # 2. Process
        Actor.log.info(f"Translating to {tgt}...")
        try:
            translation = translate_text(text, src, tgt)
            
            # 3. Save result to Dataset (The "Service" part)
            await Actor.push_data({
                "original_text": text,
                "translated_text": translation,
                "source": src,
                "target": tgt
            })
            
            await Actor.exit(status_message="Translation complete!")
            
        except Exception as e:
            await Actor.fail(status_message=f"Translation failed: {str(e)}")
