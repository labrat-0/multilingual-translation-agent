# Multilingual Translation Utility Agent Skill

## Description
This agent provides language translation as a Skill-as-a-Service for other agents. It translates text between languages, calculates the character count, and provides per-character billing. Designed for seamless integration in multi-agent workflows, it enables agents to leverage translation capabilities without building their own solutions.

## Inputs
- `text`: String. Text to be translated.
- `source_language`: String. Language code of the input text (e.g., "EN").
- `target_language`: String. Language code of the output text (e.g., "DE").
- `tone` (optional): String. Desired tone or style of translation.

## Outputs
- `translated_text`: String. Translated text in target language.
- `character_count`: Integer. Number of input characters billed.
- `language_pair`: String. Source → Target language codes.

## Pricing Model
- Charged per input character.
- Example: $0.00002 / character.
- Billing is deterministic and auditable.

## Constraints
- Translates text only; no scraping or private data processing.
- Must respect agent-to-agent calling conventions.
- Deterministic character count required for accurate billing.

## Example
Input:
```json
{
  "text": "Hello world!",
  "source_language": "EN",
  "target_language": "DE"
}

## Output
{
  "translated_text": "Hallo Welt!",
  "character_count": 12,
  "language_pair": "EN→DE"
}



---

## **3. File: translator.py**

```python
"""
Translator module for the Multilingual Translation Utility Agent.

Handles translation between languages and returns translated text.
Backend can be API-based or local model-based.
"""

def translate_text(text: str, source_language: str, target_language: str, tone: str = None) -> str:
    """
    Translate input text from source_language to target_language.
    Tone is optional and may adjust style.

    Returns:
        translated_text (str)
    """
    # Placeholder logic
    # Replace this with API call or local model translation
    translated_text = f"[{target_language} translation of '{text}']"
    return translated_text


if __name__ == "__main__":
    # Quick local test
    text = "Hello world!"
    result = translate_text(text, "EN", "DE")
    print("Translated:", result)
