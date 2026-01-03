"""
CLI entrypoint for the P1 Chatbot.

This module provides an interactive chat interface that supports both OpenAI and Gemini.
It maintains conversation history and allows continuous interaction until the user exits.
"""

import os
from dotenv import load_dotenv

load_dotenv()


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
            model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
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


def call_openai(client, model: str, messages: list[dict[str, str]]) -> str:
    """Call OpenAI API and return the assistant's response."""
    completion = client.chat.completions.create(
        model=model,
        messages=messages,
    )
    return completion.choices[0].message.content or ""


def call_gemini(client, model: str, messages: list[dict[str, str]]) -> str:
    """Call Gemini API and return the assistant's response."""
    from google.genai import types
    
    gemini_messages = []
    for msg in messages:
        role = "user" if msg["role"] == "user" else "model"
        gemini_messages.append(types.Content(role=role, parts=[types.Part(text=msg["content"])]))
    
    response = client.models.generate_content(
        model=model,
        contents=gemini_messages,
    )
    return response.text


def format_message(role: str, content: str) -> str:
    """Format the message for terminal output."""
    color = "\033[94m" if role == 'user' else "\033[92m"
    return f'{color}{role.capitalize()}: {content}\033[0m'


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
    try:
        provider, client, model = get_llm_client()
        print(f"Using {provider.upper()} ({model})")
        print("Type 'quit', 'exit', or '/quit' to end the conversation.\n")
    except Exception as e:
        print(f"Error initializing LLM client: {e}")
        return
    
    messages: list[dict[str, str]] = []
    
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
            if provider == "openai":
                assistant_text = call_openai(client, model, messages)
            else:  
                assistant_text = call_gemini(client, model, messages)
            
            print(format_message('assistant', assistant_text))
            
            messages.append({"role": "assistant", "content": assistant_text})
            
        except Exception as e:
            print(f"Error calling LLM API: {e}")
            messages.pop()


if __name__ == "__main__":
    main()
