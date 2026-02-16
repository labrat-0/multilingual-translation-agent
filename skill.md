# Multilingual Translation Agent Skill

## Description
Multi-provider translation switchboard for AI agents. Translate text between 50+ languages using LibreTranslate, OpenAI, Anthropic Claude, or Google Gemini. One stable JSON interface, multiple backends. Designed for seamless integration in multi-agent workflows as a Skill-as-a-Service.

## Inputs
- `text`: String (required). Text to be translated. Maximum 10,000 characters.
- `target_language`: String (required). ISO 639-1 code of the target language (e.g., "es", "fr", "de", "ja").
- `source_language`: String (optional). ISO 639-1 code of the source language. Defaults to auto-detect.
- `provider`: String (optional). Translation backend: "libretranslate" (default), "openai", "anthropic", "gemini".
- `api_key`: String (required). API key for the selected provider. Required for all providers including LibreTranslate.
- `model`: String (optional). Override the default model for LLM providers.
- `endpoint`: String (optional). Custom API endpoint URL.
- `temperature`: Number (optional). LLM randomness (0-1). Default: 0.
- `maxRetries`: Integer (optional). Max retry attempts. Default: 3.
- `timeoutSecs`: Integer (optional). HTTP timeout in seconds. Default: 30.

## Outputs
- `schema_version`: String. Always "1.0".
- `provider`: String. Provider used (libretranslate, openai, anthropic, gemini).
- `model`: String. Model used (empty for LibreTranslate).
- `source_language`: String. ISO 639-1 code of the source language.
- `target_language`: String. ISO 639-1 code of the target language.
- `detected_language`: String. Auto-detected source language (empty if not detected).
- `original_text`: String. The input text.
- `translated_text`: String. Translated text in target language.
- `character_count`: Integer. Number of input characters billed.
- `billing_amount`: Float. Cost based on per-character rate.
- `finish_reason`: String. LLM finish reason (empty for LibreTranslate).
- `processing_time`: Float. Time taken for the translation in seconds.

## Providers

### LibreTranslate
- API key required (sign up at libretranslate.com)
- 50+ languages
- Best for: bulk translation, prototyping, cost-sensitive workflows

### OpenAI
- Default model: gpt-4o-mini
- Supported: gpt-4o, gpt-4o-mini, gpt-4-turbo, gpt-4, gpt-3.5-turbo, o1, o1-mini, o1-preview, o3-mini
- Best for: high-quality, nuanced, context-aware translation

### Anthropic (Claude)
- Default model: claude-3-5-haiku-latest
- Supported: claude-3-5-sonnet-latest, claude-3-5-haiku-latest, claude-3-opus-latest, claude-3-sonnet-20240229, claude-3-haiku-20240307
- Best for: careful, faithful, tone-preserving translation

### Google Gemini
- Default model: gemini-2.0-flash
- Supported: gemini-2.0-flash, gemini-2.0-flash-lite, gemini-1.5-flash, gemini-1.5-pro
- Best for: fast, cost-effective LLM translation

## Pricing Model
- Charged per input character.
- $0.00002 / character (flat across all providers).
- Billing is deterministic and auditable.
- Apify PPE: $0.0005/result, free tier 25 results.

## Supported Languages
English (en), Spanish (es), French (fr), German (de), Japanese (ja), Portuguese (pt), Korean (ko), Arabic (ar), Russian (ru), Hindi (hi), Chinese Simplified (zh-hans), Chinese Traditional (zh-hant), Italian (it), Dutch (nl), Turkish (tr), Polish (pl), Swedish (sv), Danish (da), Norwegian (no), Finnish (fi), Czech (cs), Greek (el), Hebrew (he), Thai (th), Vietnamese (vi), Indonesian (id), Malay (ms), Ukrainian (uk), Romanian (ro), Hungarian (hu), Bulgarian (bg), Croatian (hr), Slovak (sk), Slovenian (sl), Lithuanian (lt), Latvian (lv), Estonian (et), Bengali (bn), Tamil (ta), Telugu (te), Marathi (mr), Urdu (ur), Persian (fa), Swahili (sw), Filipino (tl), Afrikaans (af).

## Constraints
- Maximum input length: 10,000 characters.
- Translates text only; no scraping or private data processing.
- Must respect agent-to-agent calling conventions.
- Deterministic character count required for accurate billing.
- All output keys always present (no missing/null values).

## Example

Input:
```json
{
  "text": "Hello world!",
  "source_language": "en",
  "target_language": "de",
  "provider": "openai",
  "api_key": "sk-..."
}
```

Output:
```json
{
  "schema_version": "1.0",
  "provider": "openai",
  "model": "gpt-4o-mini",
  "source_language": "en",
  "target_language": "de",
  "detected_language": "",
  "original_text": "Hello world!",
  "translated_text": "Hallo Welt!",
  "character_count": 12,
  "billing_amount": 0.00024,
  "finish_reason": "stop",
  "processing_time": 0.892
}
```
