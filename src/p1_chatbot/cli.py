"""
CLI entrypoint for the P1 Chatbot.

This module provides an interactive chat interface that supports both OpenAI and Gemini.
It maintains conversation history and allows continuous interaction until the user exits.
"""

import os
import warnings
from dotenv import load_dotenv
from .tokens import count_tokens

load_dotenv()

EXERCISE_MAX_CONTEXT_TOKENS = 4096
RESERVED_OUTPUT_TOKENS = 500
TRUNCATE_THRESHOLD_TOKENS = 3500


def get_llm_client():
    """
    Detect available API keys and return the appropriate client.
    Priority: Gemini (default for our testing), fallback to OpenAI if only OpenAI key exists.
    """
    gemini_key = os.getenv("GEMINI_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")
    
    if gemini_key:
        try:
            from google import genai
            from google.genai import types
            client = genai.Client(api_key=gemini_key)
            model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite")
            return "gemini", client, model
        except ImportError:
            print("Warning: google-genai not installed. Install with: pip install google-genai")
            if not openai_key:
                raise
    
    if openai_key:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=openai_key)
            model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
            return "openai", client, model
        except ImportError:
            print("Warning: openai not installed. Install with: pip install openai")
            raise
    
    raise ValueError(
        "No API key found. Please set GEMINI_API_KEY or OPENAI_API_KEY in your .env file."
    )


def call_openai(client, model: str, messages: list[dict[str, str]]) -> tuple[str, int, int]:
    """Call OpenAI API and return the assistant's response, prompt tokens, and completion tokens."""
    completion = client.chat.completions.create(
        model=model,
        messages=messages,
        max_tokens=RESERVED_OUTPUT_TOKENS,
    )
    assistant_text = completion.choices[0].message.content or ""
    if hasattr(completion, "usage") and completion.usage is not None:
            prompt_tokens = completion.usage.prompt_tokens
            completion_tokens = completion.usage.completion_tokens
    else:
            from .tokens import count_tokens
            prompt_tokens = count_tokens(messages, model)
            completion_tokens = count_tokens([
                {"role": "assistant", "content": assistant_text}
            ], model)
    return assistant_text, prompt_tokens, completion_tokens


def call_gemini(client, model: str, messages: list[dict[str, str]]) -> tuple[str, int, int]:
    """Call Gemini API and return the assistant's response, prompt tokens, and completion tokens."""

    conversation_history = []
    for msg in messages:
        conversation_history.append({
            "role": msg["role"],
            "content": msg["content"]
        })
    interaction = client.interactions.create(
        model=model,
        input=conversation_history,
        generation_config={
            "max_output_tokens": RESERVED_OUTPUT_TOKENS
        }
    )
    outputs = getattr(interaction, "outputs", [])
    assistant_text = ""
    for output in outputs:
        if hasattr(output, "text"):
            assistant_text = output.text
    from .tokens import count_tokens
    prompt_tokens = count_tokens(messages, model)
    completion_tokens = count_tokens([
        {"role": "assistant", "content": assistant_text}
    ], model)
    return assistant_text, prompt_tokens, completion_tokens


def format_message(role: str, content: str) -> str:
    """Format the message for terminal output."""
    color = "\033[94m" if role == 'user' else "\033[92m"
    return f'{color}{role.capitalize()}: {content}\033[0m'


def truncate_messages(messages: list[dict[str, str]], model: str) -> list[dict[str, str]]:
    """
    Truncate messages to fit within the context window budget.
    
    Removes oldest user+assistant pairs until we're under the threshold.
    
    Args:
        messages: Current message history
        model: Model name for token counting
    
    Returns:
        Truncated message list
    """
    while messages:
        input_tokens = count_tokens(messages, model)
        
        if input_tokens + RESERVED_OUTPUT_TOKENS <= EXERCISE_MAX_CONTEXT_TOKENS:
            break
        
        if input_tokens <= TRUNCATE_THRESHOLD_TOKENS:
            break

        if len(messages) >= 2:

            if messages[0].get("role") == "user" and messages[1].get("role") == "assistant":
                messages.pop(0) 
                messages.pop(0)  
                print("[context] Truncated oldest messages to fit token budget.")
            else:
                messages.pop(0)
                print("[context] Truncated oldest messages to fit token budget.")
        else:
            messages.pop(0)
            print("[context] Truncated oldest messages to fit token budget.")
    
    return messages


def main():
    """
    Main chatbot loop.
    
    Features:
    - Prompts with "You: "
    - Exits on 'quit', 'exit', or '/quit' (case-insensitive)
    - Ignores empty input
    - Maintains conversation history
    - Calls LLM API with full message history
    """
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", message="Interactions usage is experimental and may change in future versions.")
        try:
            provider, client, model = get_llm_client()
            print(f"Using {provider.upper()} ({model})")
            print("Type 'quit', 'exit', or '/quit' to end the conversation.\n")
        except Exception as e:
            print(f"Error initializing LLM client: {e}")
            return
    
    messages: list[dict[str, str]] = []
    total_cost = 0.0
    from .cost import estimate_cost

    while True:
        user_input = input("You: ").strip()

        if user_input.lower() in ["quit", "exit", "/quit"]:
            print("Goodbye!")
            break

        if not user_input:
            continue

        messages.append({"role": "user", "content": user_input})

        if client is None:
            print("LLM client is not initialized. Please check your configuration.")
            return

        try:
            messages = truncate_messages(messages, model)

            input_tokens_estimate = count_tokens(messages, model)
            print(f"Tokens (estimated input): {input_tokens_estimate}")

            if provider == "openai":
                assistant_text, prompt_tokens, completion_tokens = call_openai(client, model, messages)
            else:
                assistant_text, prompt_tokens, completion_tokens = call_gemini(client, model, messages)

            print(format_message('assistant', assistant_text))

            turn_cost = estimate_cost(model, prompt_tokens, completion_tokens)
            total_cost += turn_cost
            print(f"[usage] prompt_tokens={prompt_tokens} completion_tokens={completion_tokens}")
            print(f"[cost]  turn_usd={turn_cost:.6f} total_usd={total_cost:.6f}")


            if provider == "gemini":
                messages.append({"role": "model", "content": assistant_text})
            else:
                messages.append({"role": "assistant", "content": assistant_text})

        except Exception as e:
            print(f"Error calling LLM API: {e}")
            messages.pop()


if __name__ == "__main__":
    main()
