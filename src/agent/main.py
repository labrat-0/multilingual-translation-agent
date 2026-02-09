import asyncio
from apify import Actor
from agent.translator import translate_text
from agent.pricing import calculate_billing

async def main():
    async with Actor:
        Actor.log.info("Actor started with input")

        actor_input = await Actor.get_input()
        text = actor_input.get("text", "")
        src_lang = actor_input.get("source_language", "")
        tgt_lang = actor_input.get("target_language", "")

        Actor.log.info(f"Received text: {text}")
        translated_text = translate_text(text, src_lang, tgt_lang)
        Actor.log.info(f"Translated text: {translated_text}")

        billing = calculate_billing(text)
        Actor.log.info(f"Billing computed: {billing}")

        output = {
            "original_text": text,
            "translated_text": translated_text,
            "character_count": billing["character_count"],
            "billed_amount": billing["amount"],
            "language_pair": f"{src_lang}->{tgt_lang}"
        }
        Actor.log.info(f"Pushing output: {output}")

        await Actor.push_data(output)
        Actor.log.info("Output pushed successfully")

if __name__ == "__main__":
    asyncio.run(main())
