"""
Pricing utility for the Multilingual Translation Utility Agent.

Calculates per-character billing for agent usage.
"""

PER_CHARACTER_RATE = 0.00002  # Example: $0.00002 per character

def calculate_billing(text: str) -> dict:
    """
    Calculate billing based on input text length.

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
    bill = calculate_billing(text)
    print(f"Characters: {bill['character_count']}, Amount: ${bill['amount']}")
