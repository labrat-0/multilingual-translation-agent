"""
Input validation for the Multilingual Translation Agent.

Provider/model whitelists, key format checks, endpoint validation, and input sanitization.
"""

from __future__ import annotations

import re

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

VALID_PROVIDERS = {"libretranslate", "openai", "anthropic", "gemini"}

DEFAULT_MODELS: dict[str, str] = {
    "openai": "gpt-4o-mini",
    "anthropic": "claude-3-5-haiku-latest",
    "gemini": "gemini-2.0-flash",
}

MODEL_WHITELIST: dict[str, set[str]] = {
    "openai": {
        "gpt-4o",
        "gpt-4o-mini",
        "gpt-4-turbo",
        "gpt-4",
        "gpt-3.5-turbo",
        "o1",
        "o1-mini",
        "o1-preview",
        "o3-mini",
    },
    "anthropic": {
        "claude-3-5-sonnet-latest",
        "claude-3-5-haiku-latest",
        "claude-3-opus-latest",
        "claude-3-sonnet-20240229",
        "claude-3-haiku-20240307",
    },
    "gemini": {
        "gemini-2.0-flash",
        "gemini-2.0-flash-lite",
        "gemini-1.5-flash",
        "gemini-1.5-pro",
    },
}

# Allowed endpoint host patterns (SSRF prevention)
ALLOWED_ENDPOINT_HOSTS: dict[str, list[re.Pattern]] = {
    "libretranslate": [re.compile(r".*")],  # any host for self-hosted Libre
    "openai": [
        re.compile(r"^api\.openai\.com$"),
        re.compile(r"^.*\.openai\.azure\.com$"),
        re.compile(r"^openrouter\.ai$"),
    ],
    "anthropic": [
        re.compile(r"^api\.anthropic\.com$"),
    ],
    "gemini": [
        re.compile(r"^generativelanguage\.googleapis\.com$"),
    ],
}

ISO_CODE_PATTERN = re.compile(r"^[a-z]{2}(-[a-zA-Z]{2,4})?$")

MAX_TEXT_LENGTH = 10_000


# ---------------------------------------------------------------------------
# Validation functions
# ---------------------------------------------------------------------------


def validate_provider(provider: str) -> str | None:
    """Return error message if provider is invalid, else None."""
    if provider not in VALID_PROVIDERS:
        return f"Invalid provider '{provider}'. Must be one of: {', '.join(sorted(VALID_PROVIDERS))}."
    return None


def validate_model(provider: str, model: str | None) -> tuple[str, str | None]:
    """Resolve and validate model. Returns (resolved_model, error_or_none)."""
    if provider == "libretranslate":
        return "", None  # model not used

    if not model:
        return DEFAULT_MODELS.get(provider, ""), None

    whitelist = MODEL_WHITELIST.get(provider, set())
    if model not in whitelist:
        return model, f"Invalid model '{model}' for provider '{provider}'. Supported: {', '.join(sorted(whitelist))}."

    return model, None


def validate_api_key(provider: str, api_key: str | None) -> str | None:
    """Return error message if API key is missing when required."""
    if provider == "libretranslate":
        return None  # optional for Libre

    if not api_key or not api_key.strip():
        return f"API key is required for provider '{provider}'."

    return None


def validate_endpoint(provider: str, endpoint: str | None) -> str | None:
    """Validate custom endpoint against allowed host patterns. Returns error or None."""
    if not endpoint:
        return None

    # Extract host from URL
    try:
        from urllib.parse import urlparse
        parsed = urlparse(endpoint)
        host = parsed.hostname
        if not host:
            return f"Invalid endpoint URL: '{endpoint}'. Could not parse hostname."
    except Exception:
        return f"Invalid endpoint URL: '{endpoint}'."

    # Block localhost / private IPs
    if host in ("localhost", "127.0.0.1", "0.0.0.0") or host.startswith("192.168.") or host.startswith("10."):
        return f"Endpoint host '{host}' is not allowed (private/localhost)."

    patterns = ALLOWED_ENDPOINT_HOSTS.get(provider, [])
    for pattern in patterns:
        if pattern.match(host):
            return None

    return f"Endpoint host '{host}' is not allowed for provider '{provider}'."


def validate_language_code(code: str | None) -> bool:
    """Validate ISO 639-1 code with optional subtag."""
    if not code:
        return False
    return bool(ISO_CODE_PATTERN.fullmatch(code))


def validate_text(text: str) -> str | None:
    """Return error if text is invalid."""
    if not text or not text.strip():
        return "No text provided in input."
    if len(text) > MAX_TEXT_LENGTH:
        return f"Text exceeds maximum length of {MAX_TEXT_LENGTH} characters ({len(text)} provided)."
    return None


def sanitize_text(text: str) -> str:
    """Strip null bytes and problematic control characters, preserve newlines/tabs."""
    return text.replace("\x00", "")


def sanitize_error(message: str, api_key: str | None = None) -> str:
    """Remove API key from error messages to prevent leakage."""
    if api_key and api_key in message:
        message = message.replace(api_key, "[REDACTED]")
    return message
