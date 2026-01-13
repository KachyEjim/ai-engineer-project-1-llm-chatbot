# ai-engineer-project-1-llm-chatbot

## Overview

This project is a modular, production-ready LLM-powered chatbot built for AI engineering learning and demonstration. It supports both OpenAI and Gemini models, robust error handling, configuration via environment variables, and cost estimation. The code is organized for clarity, extensibility, and reliability.

**What I learned:**

- How to structure AI projects for maintainability
- Implementing robust error handling and retry logic
- Managing configuration and secrets securely
- Token counting and cost estimation for LLM APIs
- Writing clear documentation for reproducibility

## Features

- Interactive CLI chatbot with conversation history
- Supports OpenAI and Gemini (Google) models
- Modular codebase with separation of concerns
- Robust error handling (auth, rate limits, network)
- Automatic retries with exponential backoff
- Token counting and cost estimation
- Configuration via environment variables
- Easy setup and usage

## Setup

1. Create and activate a virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```
4. Set your API keys and configuration in `.env`:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   GEMINI_API_KEY=your_gemini_api_key_here
   GEMINI_MODEL=gemini-2.5-flash-lite
   P1_MODEL=gpt-4o-mini
   P1_TEMPERATURE=0.1
   P1_MAX_TOKENS=500
   ```

**Do not commit your `.env` file to version control.**

## Usage

To run the chatbot CLI:

```bash
source .venv/bin/activate
python -m src.p1_chatbot.cli
```

Type `quit`, `exit`, or `/quit` to end the conversation.

## Configuration

The chatbot is configured via environment variables (see `.env`). You can change these at any time without code edits:

- `P1_MODEL`: Model name (default: `gpt-4o-mini`)
- `P1_TEMPERATURE`: Sampling temperature (default: `0.1`)
- `P1_MAX_TOKENS`: Max tokens for each response (default: `500`)
- `OPENAI_API_KEY`: Your OpenAI API key
- `GEMINI_API_KEY`: Your Gemini API key
- `GEMINI_MODEL`: Gemini model name (default: `gemini-2.5-flash-lite`)

## Architecture

- `cli.py`: CLI entrypoint, user I/O, orchestration
- `config.py`: Loads environment variables and defines defaults
- `llm_client.py`: LLM API wrappers, error handling, retries
- `tokens.py`: Token counting utilities
- `cost.py`: Pricing and cost estimation
- `prompts.py`: System prompt(s)

## Troubleshooting

- **Missing API key:** Ensure you have copied `.env.example` to `.env` and added your API key.
- **venv not activated:** Run `source .venv/bin/activate` before installing dependencies or running scripts.
- **Network or rate limit errors:** The chatbot will retry automatically and print clear error messages.

## Pricing source

- Model: gpt-4o-mini

  - Price per 1,000 input tokens: $0.0005
  - Price per 1,000 output tokens: $0.0015
  - Date recorded: 2026-01-09
  - Source: https://openai.com/pricing

- Model: gemini-2.5-flash-lite
  - Price per 1,000 input tokens: $0.00025
  - Price per 1,000 output tokens: $0.0005
  - Date recorded: 2026-01-09
  - Source: https://cloud.google.com/vertex-ai/generative-ai/pricing

---

**Clone, install, set .env, and run the chatbot using only this README.**
