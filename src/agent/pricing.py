"""
Pricing utility for the Multilingual Translation Agent.

Flat per-character billing regardless of provider.
Apify PPE pricing ($0.0005/result) is handled at the platform level.
This module calculates the internal character-based billing for audit/transparency.
"""

from __future__ import annotations

PER_CHARACTER_RATE = 0.00002  # $0.00002 per character (all providers)


def calculate_billing(text: str, provider: str = "libretranslate") -> dict:
    """
    Calculate billing based on input text length.

    Args:
        text: The input text being translated.
        provider: Translation provider (unused for now -- flat rate).

    Returns:
        dict: {
            'character_count': int,
            'amount': float
        }
    """
    count = len(text)
    amount = round(count * PER_CHARACTER_RATE, 6)
    return {"character_count": count, "amount": amount}


if __name__ == "__main__":
    text = "Hello world!"
    bill = calculate_billing(text, "openai")
    print(f"Characters: {bill['character_count']}, Amount: ${bill['amount']}")
