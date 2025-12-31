# ai-engineer-project-1-llm-chatbot

## Project

This project is an LLM-powered chatbot designed to demonstrate core AI engineering skills. By Day 7, it will feature interactive conversations, well made prompts, and basic integrations with external APIs to perform even more tasks. The chatbot will be modular, extensible, scalable and serve as a foundation for more advanced AI-driven applications.

## Provider

Currently using: OpenAI

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
3. Copy the example environment file and add your API key:
   ```bash
   cp .env.example .env
   # Edit .env to add your API key
   ```

## Running Day 1

To run the Day 1 script:

```bash
python src/day_01/day_01_hello_world.py
```

## Troubleshooting

- **Missing API key:** Ensure you have copied `.env.example` to `.env` and added your API key.
- **venv not activated:** Run `source .venv/bin/activate` before installing dependencies or running scripts.

## Commit and push

Suggested commit message:

```
chore: initialize project structure for day 01
```
