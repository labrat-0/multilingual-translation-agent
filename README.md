# Multilingual Translation Agent

Multi-provider translation switchboard for AI agents. Translate text using LibreTranslate, OpenAI, Anthropic Claude, or Google Gemini through one stable JSON interface. MCP-ready for AI agent integration.

> **API Key Required:** This actor requires a valid API key from one of the supported providers to run. Get a key from [LibreTranslate](https://portal.libretranslate.com), [OpenAI](https://platform.openai.com), [Anthropic](https://console.anthropic.com), or [Google AI Studio](https://aistudio.google.com).

## Features

- **4 translation providers** behind one interface: LibreTranslate, OpenAI, Anthropic, Gemini
- **LLM-quality translation**: OpenAI, Anthropic, and Gemini for high-quality, context-aware output
- **Stable JSON output**: `schema_version: "1.0"`, no missing keys, predictable contract
- ISO 639-1 language validation with auto-detect support
- 50+ supported languages
- Per-character billing with deterministic cost tracking
- Configurable model, temperature, endpoint, retries, and timeout
- MCP-ready for agent-to-agent workflows

## Provider Comparison

| Provider | Cost | Quality | API Key Required | Char Limit | Best For |
|----------|------|---------|------------------|------------|----------|
| LibreTranslate | From $29/mo | Good | Yes ([get key](https://portal.libretranslate.com)) | 2,000/request | Bulk translation, prototyping |
| OpenAI (gpt-4o-mini) | Pay-per-token | Excellent | Yes | 10,000 | High-quality, nuanced text |
| Anthropic (claude-3-5-haiku) | Pay-per-token | Excellent | Yes | 10,000 | Careful, faithful translation |
| Google Gemini (gemini-2.0-flash) | Free tier available | Excellent | Yes | 10,000 | Fast, cost-effective LLM |

## Requirements

- Python 3.12+
- Apify platform account (for running as Actor)
- API key for your selected provider (LibreTranslate, OpenAI, Anthropic, or Gemini)

Install dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

### Actor Inputs

Defined in `.actor/INPUT_SCHEMA.json`:

| Input | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `text` | string | Yes | -- | Text to translate (max 10,000 chars; 2,000 for LibreTranslate) |
| `target_language` | string | Yes | `es` | ISO 639-1 target code |
| `source_language` | string | No | auto-detect | ISO 639-1 source code |
| `provider` | enum | No | `libretranslate` | `libretranslate`, `openai`, `anthropic`, `gemini` |
| `api_key` | string | Yes | -- | API key for the selected provider |
| `model` | string | No | per-provider default | Override default model |
| `endpoint` | string | No | -- | Custom API endpoint URL |
| `temperature` | number | No | `0` | LLM randomness (0-1) |
| `maxRetries` | integer | No | `3` | Max retry attempts |
| `timeoutSecs` | integer | No | `30` | HTTP timeout in seconds |

### Environment Variables

For LibreTranslate, you can optionally override the default endpoint and API key via environment variables:
- `LIBRETRANSLATE_URL` -- your LibreTranslate endpoint (defaults to `https://libretranslate.com/translate`)
- `LIBRETRANSLATE_API_KEY` -- your LibreTranslate API key

## Usage

### Local (CLI)
```bash
APIFY_TOKEN=your-token apify run
```

### Example Inputs

**LibreTranslate:**
```json
{
  "text": "How are you today, friend?",
  "target_language": "es",
  "provider": "libretranslate",
  "api_key": "your-libretranslate-api-key"
}
```

**OpenAI:**
```json
{
  "text": "How are you today, friend?",
  "target_language": "de",
  "provider": "openai",
  "api_key": "sk-...",
  "model": "gpt-4o-mini"
}
```

**Anthropic:**
```json
{
  "text": "How are you today, friend?",
  "target_language": "fr",
  "provider": "anthropic",
  "api_key": "sk-ant-...",
  "model": "claude-3-5-haiku-latest"
}
```

**Google Gemini:**
```json
{
  "text": "How are you today, friend?",
  "target_language": "ja",
  "provider": "gemini",
  "api_key": "AIza...",
  "model": "gemini-2.0-flash"
}
```

### Output Schema (stable, all keys always present)

```json
{
  "schema_version": "1.0",
  "provider": "openai",
  "model": "gpt-4o-mini",
  "source_language": "auto",
  "target_language": "de",
  "detected_language": "",
  "original_text": "How are you today, friend?",
  "translated_text": "Wie geht es dir heute, Freund?",
  "character_count": 26,
  "billing_amount": 0.00052,
  "finish_reason": "stop",
  "processing_time": 1.234
}
```

## Architecture

- `src/agent/main.py` -- Actor entry point, input validation, orchestration, stable output
- `src/agent/translator.py` -- Multi-provider translation engine (LibreTranslate, OpenAI, Anthropic, Gemini)
- `src/agent/validation.py` -- Input validation, provider/model whitelists, SSRF prevention
- `src/agent/pricing.py` -- Deterministic per-character billing ($0.00002/char)
- `skill.md` -- Machine-readable skill contract for agent discovery

## Supported Models

**OpenAI:** gpt-4o, gpt-4o-mini, gpt-4-turbo, gpt-4, gpt-3.5-turbo, o1, o1-mini, o1-preview, o3-mini

**Anthropic:** claude-3-5-sonnet-latest, claude-3-5-haiku-latest, claude-3-opus-latest, claude-3-sonnet-20240229, claude-3-haiku-20240307

**Gemini:** gemini-2.0-flash, gemini-2.0-flash-lite, gemini-1.5-flash, gemini-1.5-pro

## Use Cases

- **Multilingual ETL**: Translate scraped content into target languages for downstream pipelines
- **Localization**: Translate UI strings, product descriptions, support articles
- **Support triage**: Auto-translate incoming tickets to a common language
- **Cross-lingual search**: Translate queries before searching foreign-language datasets
- **Agent messaging**: Agents translate their own output for multilingual users
- **AI agent tooling**: Expose as MCP tool for autonomous translation in agent workflows

## Troubleshooting

- **401/403 error**: Check your API key for the selected provider
- **400 error**: Verify language codes are valid ISO 639-1 (e.g., `en`, `es`, `zh-hans`)
- **Empty response**: Provider may not support the requested language pair or model
- **Timeout**: Increase `timeoutSecs` or check provider status
- **Invalid model**: Check Supported Models section for the whitelist per provider

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

AI agents can use this actor to translate text between 50+ languages using any of 4 providers, auto-detect source languages, and integrate multilingual translation into agent workflows -- all as a callable MCP tool.
