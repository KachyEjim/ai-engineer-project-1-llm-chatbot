from dotenv import load_dotenv
import os
import sys

load_dotenv()

PROMPT = "Explain the difference between an AI Engineer and a Software Engineer in one sentence."

def call_openai():
    try:
        from openai import OpenAI
    except ImportError:
        print("ERROR: openai package not installed. Please install it with 'pip install openai'.")
        sys.exit(1)
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("ERROR: OPENAI_API_KEY is not set. Create a .env file from .env.example and add your key.")
        sys.exit(1)
    client = OpenAI(api_key=api_key)
    try:
        response = client.responses.create(model="gpt-4o-mini", input=PROMPT)
        print(response.output_text)
        sys.exit(0)
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)

def call_gemini():
    try:
        from google import genai
    except ImportError:
        print("ERROR: google-genai package not installed. Please install it with 'pip install google-genai'.")
        sys.exit(1)
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("ERROR: GEMINI_API_KEY is not set. Create a .env file from .env.example and add your key.")
        sys.exit(1)
    model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(model=model_name, contents=PROMPT)
        print(response.text)
        sys.exit(0)
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)

# Default: call Gemini
if __name__ == "__main__":
    call_gemini()
