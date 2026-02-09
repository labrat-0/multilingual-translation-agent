from apify import Actor
from langdetect import detect, DetectorFactory
from .translator import translate_text

# Ensures the detection is consistent every time
DetectorFactory.seed = 0 

async def main():
    async with Actor:
        actor_input = await Actor.get_input() or {}
        text = actor_input.get("text")
        target_lang = actor_input.get("target_language", "FR").lower()
        source_lang = actor_input.get("source_language") # Might be None

        if not text:
            await Actor.fail(status_message="Missing 'text' input.")
            return

        # --- AUTO-DETECTION LOGIC ---
        if not source_lang or source_lang.strip() == "":
            Actor.log.info("Source language not provided. Detecting...")
            try:
                source_lang = detect(text)
                Actor.log.info(f"Detected language: {source_lang.upper()}")
            except Exception:
                source_lang = "en" # Fallback to English if detection fails
                Actor.log.warning("Detection failed, falling back to English.")
        else:
            source_lang = source_lang.lower()
        # ----------------------------

        # If source and target are the same, skip translation
        if source_lang == target_lang:
            await Actor.push_data({"translation": text, "note": "Source and target are the same."})
            return

        try:
            translation = translate_text(text, source_lang, target_lang)
            await Actor.push_data({
                "detected_source": source_lang.upper(),
                "target": target_lang.upper(),
                "original": text,
                "translation": translation
            })
        except Exception as e:
            await Actor.fail(status_message=f"Translation Error: {str(e)}")
