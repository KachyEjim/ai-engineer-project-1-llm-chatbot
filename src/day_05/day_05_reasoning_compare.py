"""
Zero-shot vs. step-by-step (CoT) comparison for Day 5.
Prints both model responses for the same math word problem.
"""


import os
from dotenv import load_dotenv
load_dotenv()

# Set PROVIDER to "openai" or "gemini"
PROVIDER = os.getenv("REASONING_PROVIDER", "openai")

QUESTION = "A coffee shop sells cups for $3 each and muffins for $2 each. If you buy 4 cups and 5 muffins, how much do you spend in total?"

if PROVIDER == "openai":
    from openai import OpenAI
    MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    API_KEY = os.getenv("OPENAI_API_KEY")
    client = OpenAI(api_key=API_KEY)
    # Zero-shot
    zero_shot_messages = [
        {"role": "user", "content": QUESTION}
    ]
    zero_shot_response = client.chat.completions.create(
        model=MODEL,
        messages=zero_shot_messages, # type: ignore
        max_tokens=100,
        temperature=0.1,
    )
    # Step-by-step (CoT)
    cot_messages = [
        {"role": "user", "content": "Explain your reasoning step-by-step, then give the final answer.\n\n" + QUESTION}
    ]
    cot_response = client.chat.completions.create(
        model=MODEL,
        messages=cot_messages, # type: ignore
        max_tokens=200,
        temperature=0.1,
    )
    print("=== ZERO SHOT ===")
    print(zero_shot_response.choices[0].message.content)
    print("\n=== STEP BY STEP ===")
    print(cot_response.choices[0].message.content)
elif PROVIDER == "gemini":
    GEMINI_KEY = os.getenv("GEMINI_API_KEY")
    MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite")
    from google import genai
    from google.genai import types
    client = genai.Client(api_key=GEMINI_KEY)
    # Zero-shot
    zero_shot_prompt = QUESTION
    zero_shot_messages = [types.Content(role="user", parts=[types.Part(text=zero_shot_prompt)])]
    zero_shot_response = client.models.generate_content(
        model=MODEL,
        contents=zero_shot_messages,
        config=types.GenerateContentConfig(max_output_tokens=100, temperature=0.1)
    )
    # Step-by-step (CoT)
    cot_prompt = "Explain your reasoning step-by-step, then give the final answer.\n\n" + QUESTION
    cot_messages = [types.Content(role="user", parts=[types.Part(text=cot_prompt)])]
    cot_response = client.models.generate_content(
        model=MODEL,
        contents=cot_messages,
        config=types.GenerateContentConfig(max_output_tokens=200, temperature=0.1)
    )
    print("=== ZERO SHOT ===")
    print(zero_shot_response.text)
    print("\n=== STEP BY STEP ===")
    print(cot_response.text)
else:
    print("Error: PROVIDER must be 'openai' or 'gemini'.")