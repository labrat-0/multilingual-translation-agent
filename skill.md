# Multilingual Translation Utility Agent Skill

## Description
This agent provides language translation as a Skill-as-a-Service for other agents. It translates text between languages, calculates the character count, and provides per-character billing. Designed for seamless integration in multi-agent workflows, it enables agents to leverage translation capabilities without building their own solutions.

## Inputs
- `text`: String (required). Text to be translated. Maximum 5000 characters.
- `target_language`: String (required). ISO 639-1 code of the target language (e.g., "es", "fr", "de").
- `source_language`: String (optional). ISO 639-1 code of the source language. Defaults to auto-detect.

## Outputs
- `original_text`: String. The input text.
- `translated_text`: String. Translated text in target language.
- `source_language`: String. ISO 639-1 code of the source language.
- `target_language`: String. ISO 639-1 code of the target language.
- `character_count`: Integer. Number of input characters billed.
- `billing_amount`: Float. Cost based on per-character rate.
- `translation_time`: Float. Time taken for the translation in seconds.

## Pricing Model
- Charged per input character.
- $0.00002 / character.
- Billing is deterministic and auditable.

## Supported Languages
English (en), Spanish (es), French (fr), German (de), Japanese (ja), Portuguese (pt), Korean (ko), Arabic (ar), Russian (ru), Hindi (hi), Chinese Simplified (zh-Hans), Chinese Traditional (zh-Hant), Italian (it), Dutch (nl), Turkish (tr), and 35+ more via LibreTranslate.

## Constraints
- Maximum input length: 5000 characters.
- Translates text only; no scraping or private data processing.
- Must respect agent-to-agent calling conventions.
- Deterministic character count required for accurate billing.

## Example

Input:
```json
{
  "text": "Hello world!",
  "source_language": "en",
  "target_language": "de"
}
```

Output:
```json
{
  "original_text": "Hello world!",
  "translated_text": "Hallo Welt!",
  "source_language": "en",
  "target_language": "de",
  "character_count": 12,
  "billing_amount": 0.00024,
  "translation_time": 0.35
}
```
