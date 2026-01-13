# Project 1 chatbot configuration

import os
from dotenv import load_dotenv

load_dotenv()
P1_MODEL = os.getenv("P1_MODEL", "gpt-4o-mini")
P1_TEMPERATURE = float(os.getenv("P1_TEMPERATURE", "0.1"))
P1_MAX_TOKENS = int(os.getenv("P1_MAX_TOKENS", "500"))
EXERCISE_MAX_CONTEXT_TOKENS = 4096
RESERVED_OUTPUT_TOKENS = 500
TRUNCATE_THRESHOLD_TOKENS = 3500

GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
