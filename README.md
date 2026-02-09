# Multilingual Translation Utility Agent

A Python-based translation utility agent designed to be used by other agents
and automated workflows. The agent translates text between languages and
returns deterministic usage metrics suitable for per-character billing.

## Purpose

This project provides a reusable, infrastructure-level translation agent
that can be composed into larger agent systems such as scrapers, customer
support agents, content localization pipelines, and market research tools.

## Features

- Multilingual text translation
- Explicit source and target language control
- Deterministic character counting for billing
- Clean, predictable inputs and outputs
- Designed for agent-to-agent usage

## Inputs

- `text`: Text to translate
- `source_language`: Language code of the input text
- `target_language`: Language code of the output text

## Outputs

- `translated_text`: Translated content
- `character_count`: Number of billable input characters
- `language_pair`: Source and target language codes

## Pricing Model

This agent is designed to support per-character pricing.
Billing is calculated based on the number of input characters processed per request.

Example:
- Input characters: 1,250
- Billed characters: 1,250

## Constraints

- Text-only translation
- No personal data handling
- Deterministic, auditable usage reporting
- Translation of user-provided content only

## Status

Initial scaffold. Translation backend and execution logic are under active development.
