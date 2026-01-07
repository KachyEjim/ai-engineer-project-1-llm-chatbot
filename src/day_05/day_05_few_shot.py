"""
Few-shot review classifier for Day 5.
Prints Positive or Negative for the test review.
Supports both OpenAI and Gemini, switchable by PROVIDER variable.
"""
import os
from dotenv import load_dotenv
load_dotenv()

# Set PROVIDER to "openai" or "gemini"
PROVIDER = os.getenv("FEW_SHOT_PROVIDER", "openai")

TEST_REVIEW = "The cinematography was nice but the story felt flat and predictable."

if PROVIDER == "openai":
    from openai import OpenAI
    MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    API_KEY = os.getenv("OPENAI_API_KEY")
    client = OpenAI(api_key=API_KEY)
    FEW_SHOT_EXAMPLES = [
        {"role": "user", "content": "Review: I loved this movie. Great pacing and strong acting. Label it as Positive or Negative."},
        {"role": "assistant", "content": "Positive"},
        {"role": "user", "content": "Review: Not worth my time. The plot was confusing and boring. Label it as Positive or Negative."},
        {"role": "assistant", "content": "Negative"},
        {"role": "user", "content": "Review: Surprisingly good. I would watch it again. Label it as Positive or Negative."},
        {"role": "assistant", "content": "Positive"},
    ]
    messages = FEW_SHOT_EXAMPLES + [
        {"role": "user", "content": f"Review: {TEST_REVIEW} Label it as Positive or Negative."}
    ]
    response = client.chat.completions.create(
        model=MODEL,
        messages=messages, # type: ignore
        max_tokens=1,
        temperature=0.1,
    )
    print(response.choices[0].message.content)
elif PROVIDER == "gemini":
    GEMINI_KEY = os.getenv("GEMINI_API_KEY")
    MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite")
    from google import genai
    from google.genai import types
    client = genai.Client(api_key=GEMINI_KEY)
    FEW_SHOT_PROMPT = """
Review: I loved this movie. Great pacing and strong acting.
Label: Positive

Review: Not worth my time. The plot was confusing and boring.
Label: Negative

Review: Surprisingly good. I would watch it again.
Label: Positive

Review: The cinematography was nice but the story felt flat and predictable.
Label:
"""
    gemini_messages = [types.Content(role="user", parts=[types.Part(text=FEW_SHOT_PROMPT)])]
    response = client.models.generate_content(
        model=MODEL,
        contents=gemini_messages,
        config=types.GenerateContentConfig(max_output_tokens=5, temperature=0.1)
    )
    print(response.text)
else:
    print("Error: PROVIDER must be 'openai' or 'gemini'.")
