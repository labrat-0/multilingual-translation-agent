import asyncio
from apify import Actor

from agent.translator import translate_text
from agent.pricing import calculate_billing

async def main():
    async with Actor:
        Actor.log.info("Actor started — getting input")

        # Get run input
        actor_input = await Actor.get_input()
        Actor.log.info(f"Input received: {actor_input}")

        if not actor_input:
            Actor.log.error("No input provided!")
            return

        text = actor_input.get("text")
        src_lang = actor_input.get("source_language")
        tgt_lang = actor_input.get("target_language")

        if not text or not src_lang or not tgt_lang:
            Actor.log.error("Missing required input fields")
            return

        Actor.log.info(f"Translating text: {text}")

        translated_text = translate_text(text, src_lang, tgt_lang)
        Actor.log.info(f"Translated text: {translated_text}")

        billing = calculate_billing(text)
        Actor.log.info(f"Billing: {billing}")

        output = {
            "original_text": text,
            "translated_text": translated_text,
            "character_count": billing["character_count"],
            "billed_amount": billing["amount"],
            "language_pair": f"{src_lang}->{tgt_lang}",
        }
        Actor.log.info(f"Pushing output: {output}")

        await Actor.push_data(output)
        Actor.log.info("Data pushed to default dataset")

if __name__ == "__main__":
    asyncio.run(main())
