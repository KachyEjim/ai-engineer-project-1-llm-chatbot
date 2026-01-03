# ai-engineer-project-1-llm-chatbot

## Project

This project is an LLM-powered chatbot designed to demonstrate core AI engineering skills. By Day 7, it will feature interactive conversations, well made prompts, and basic integrations with external APIs to perform even more tasks. The chatbot will be modular, extensible, scalable and serve as a foundation for more advanced AI-driven applications.

## Provider

Currently using: OpenAI and Gemini (default Gemini model: gemini-2.5-flash)

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
4. Set your API keys in `.env`:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   GEMINI_API_KEY=your_gemini_api_key_here
   GEMINI_MODEL=gemini-2.5-flash
   ```

**Do not commit your `.env` file to version control.**

## Running Day 1

To run the Day 1 script:

```bash
source .venv/bin/activate
python -m src.day_01.day_01_hello_world
```

This will print a one-sentence answer from the LLM to stdout.

## Running Day 2

To run the interactive chatbot CLI:

```bash
source .venv/bin/activate
python -m src.p1_chatbot.cli
```

This will start an interactive chat session with conversation history. Type `quit`, `exit`, or `/quit` to end the conversation.

## Troubleshooting

- **Missing API key:** Ensure you have copied `.env.example` to `.env` and added your API key.
- **venv not activated:** Run `source .venv/bin/activate` before installing dependencies or running scripts.
