import asyncio
from apify import Actor
from translator import translate_text
from pricing import calculate_billing

async def main():
    async with Actor:
        # Get input provided to the Actor run
        actor_input = await Actor.get_input() or {}

        # Read required fields
        text = actor_input.get("text", "")
        src_lang = actor_input.get("source_language", "")
        tgt_lang = actor_input.get("target_language", "")

        # Perform translation
        translated_text = translate_text(text, src_lang, tgt_lang)

        # Calculate billing based on input text
        billing = calculate_billing(text)

        # Prepare output object
        output = {
            "original_text": text,
            "translated_text": translated_text,
            "character_count": billing["character_count"],
            "billed_amount": billing["amount"],
            "language_pair": f"{src_lang}->{tgt_lang}"
        }

        # Push output to default dataset
        await Actor.push_data(output)

if __name__ == "__main__":
    asyncio.run(main())
