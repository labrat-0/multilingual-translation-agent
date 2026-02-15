# Multilingual Translation Agent

Apify Actor that provides fast text translation powered by LibreTranslate. Accepts ISO 639-1 language codes, validates inputs, and returns translated text with per-character billing data. Supports both self-hosted and public LibreTranslate endpoints. MCP-ready for AI agent integration.

## Features
- ISO 639-1 language validation with optional auto-detect
- 50+ supported languages via LibreTranslate
- Configurable backend: self-hosted VPS or public API
- Character counting and deterministic billing
- Structured JSON output with timing metadata
- Secure API key handling via environment variables

## Requirements
- Python 3.11+
- Apify platform account (for running as Actor)
- LibreTranslate instance (self-hosted or public)

Install dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

### Actor Inputs
Defined in `.actor/INPUT_SCHEMA.json`:
- `text` (string, required) -- text to translate, max 5000 characters
- `target_language` (string, required) -- ISO 639-1 target code (e.g., `es`, `fr`, `zh-hans`)
- `source_language` (string, optional) -- ISO 639-1 source code, defaults to auto-detect
- `api_key` (string, optional) -- only needed if using your own LibreTranslate instance

### Environment Variables
Set these in Apify Actor settings for self-hosted mode:
- `LIBRETRANSLATE_URL` -- your LibreTranslate endpoint (e.g., `https://translate.yourdomain.com/translate`)
- `LIBRETRANSLATE_API_KEY` -- server-side API key for your instance

If not set, the actor falls back to the public LibreTranslate API.

## Usage
### Local (CLI)
```bash
APIFY_TOKEN=your-token apify run
```

### Example Input
```json
{
  "text": "How are you today my friend?",
  "target_language": "es"
}
```

### Example Output
```json
{
  "original_text": "How are you today my friend?",
  "translated_text": "¿Cómo estás hoy mi amigo?",
  "character_count": 29,
  "billing_amount": 0.00058,
  "source_language": "auto",
  "target_language": "es",
  "translation_time": 0.482
}
```

## Architecture
- `src/agent/main.py` -- Actor entry point, input validation, orchestration
- `src/agent/translator.py` -- LibreTranslate API client with configurable endpoint
- `src/agent/pricing.py` -- Deterministic per-character billing ($0.00002/char)
- `skill.md` -- Machine-readable skill contract for agent discovery

## Troubleshooting
- **401/403 error**: check `LIBRETRANSLATE_API_KEY` or actor `api_key` input
- **400 error**: verify language codes are valid ISO 639-1 (e.g., `en`, `es`, `zh-hans`)
- **Empty response**: LibreTranslate may not support the requested language pair
- **Timeout**: increase `TIMEOUT_SECONDS` in translator.py or check VPS health

## License
See `LICENSE` file for details.

---

## MCP Integration

This actor works as an MCP tool through Apify's hosted MCP server. No custom server needed.

- **Endpoint:** `https://mcp.apify.com?tools=labrat011/multilingual-translation-agent`
- **Auth:** `Authorization: Bearer <APIFY_TOKEN>`
- **Transport:** Streamable HTTP
- **Works with:** Claude Desktop, Cursor, VS Code, Windsurf, Warp, Gemini CLI

**Example MCP config (Claude Desktop / Cursor):**

```json
{
    "mcpServers": {
        "multilingual-translation-agent": {
            "url": "https://mcp.apify.com?tools=labrat011/multilingual-translation-agent",
            "headers": {
                "Authorization": "Bearer <APIFY_TOKEN>"
            }
        }
    }
}
```

AI agents can use this actor to translate text between 50+ languages, auto-detect source languages, and integrate multilingual translation into agent workflows -- all as a callable MCP tool.
