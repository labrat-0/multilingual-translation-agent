# Multilingual Translation Agent

Apify Actor that provides fast text translation powered by LibreTranslate. It accepts source/target language codes, validates inputs, and returns translated text plus per-character billing data. LibreTranslate now requires an API key; supply it through the `api_key` input field.

## Features
- ISO 639-1 language validation with optional auto-detect
- LibreTranslate HTTP API integration with API key support
- Character counting and billing via `pricing.calculate_billing`
- Structured Apify dataset output with timing metadata

## Requirements
- Python 3.11+
- Apify platform account (for running as Actor)
- LibreTranslate API key (get one at https://portal.libretranslate.com)

Install dependencies:
```bash
pip install -r requirements.txt
```

## Configuration
Inputs are defined in `.actor/INPUT_SCHEMA.json`:
- `text` (string, required)
- `target_language` (ISO 639-1 code, required)
- `source_language` (ISO 639-1 code, optional, defaults to auto)
- `api_key` (string, optional but required by LibreTranslate)

## Usage
### Local (CLI)
```bash
APIFY_TOKEN=your-token apify run
```
Provide an input JSON file with the fields above, or set them via Apify console.

### Example Input
```json
{
  "text": "How are you today my friend?",
  "source_language": "en",
  "target_language": "es",
  "api_key": "YOUR_LIBRETRANSLATE_KEY"
}
```

### Example Output
```json
{
  "original_text": "How are you today my friend?",
  "translated_text": "¿Cómo estás hoy mi amigo?",
  "character_count": 29,
  "billing_amount": 0.00058,
  "source_language": "en",
  "target_language": "es",
  "translation_time": 0.48
}
```

## Development Notes
- Actor entry point: `src/agent/main.py`
- Translation logic: `src/agent/translator.py`
- Pricing logic: `src/agent/pricing.py`
- Dependencies pinned in `requirements.txt` for reproducible builds

## Troubleshooting
- **400 error mentioning API key**: ensure `api_key` is included and valid.
- **Invalid language code**: use lowercase ISO 639-1 codes (e.g., `en`, `es`).
- **Large payload rejection**: inputs above 5000 characters are rejected by design.

## License
See `LICENSE` file for details.