# Import system prompt
from .prompts import DEFAULT_SYSTEM_PROMPT
"""
CLI entrypoint for the P1 Chatbot.

This module provides an interactive chat interface that supports both OpenAI and Gemini.
It maintains conversation history and allows continuous interaction until the user exits.
"""

import os
import warnings
from .tokens import count_tokens
from .config import (
    EXERCISE_MAX_CONTEXT_TOKENS,
    RESERVED_OUTPUT_TOKENS,
    TRUNCATE_THRESHOLD_TOKENS,
    GEMINI_MODEL,
    OPENAI_MODEL,
    GEMINI_API_KEY,
    OPENAI_API_KEY,
    P1_MODEL,
    P1_TEMPERATURE,
    P1_MAX_TOKENS
)



# Import LLM client logic from llm_client.py
from .llm_client import get_llm_client, call_openai, call_gemini, create_chat_completion


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

    # Set up message history with system prompt in correct role
    if provider == "gemini":
        messages = [{"role": "user", "content": DEFAULT_SYSTEM_PROMPT}]
    else:
        messages = [{"role": "system", "content": DEFAULT_SYSTEM_PROMPT}]
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
                assistant_text, prompt_tokens, completion_tokens = create_chat_completion(
                    messages,
                    model=P1_MODEL,
                    temperature=P1_TEMPERATURE,
                    max_tokens=P1_MAX_TOKENS
                )
            else:
                assistant_text, prompt_tokens, completion_tokens = call_gemini(client, model, messages)

            print(format_message('assistant', assistant_text))

            safe_prompt_tokens = prompt_tokens if prompt_tokens is not None else 0
            safe_completion_tokens = completion_tokens if completion_tokens is not None else 0
            turn_cost = estimate_cost(model, safe_prompt_tokens, safe_completion_tokens)
            total_cost += turn_cost
            print(f"[usage] prompt_tokens={safe_prompt_tokens} completion_tokens={safe_completion_tokens}")
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
