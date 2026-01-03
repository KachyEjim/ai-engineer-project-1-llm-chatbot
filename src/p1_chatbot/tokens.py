"""
Token counting utilities for chatbot message history.

This module provides token counting for both OpenAI and Gemini models.
The counts are estimates and may differ slightly from the actual API token usage.
"""

import tiktoken


def count_tokens(messages: list[dict[str, str]], model: str) -> int:
    """
    Estimate the number of tokens in a message list.
    
    This is an approximation because:
    - The actual tokenization may vary slightly between models
    - API overhead tokens (e.g., message formatting) are not included
    - Gemini uses a different tokenizer than OpenAI
    
    Args:
        messages: List of message dicts with 'role' and 'content' keys
        model: Model name (e.g., 'gpt-4o-mini', 'gemini-2.5-flash')
    
    Returns:
        Estimated token count as an integer
    """
    if "gemini" in model.lower():
        return _count_tokens_gemini(messages, model)
    else:
        return _count_tokens_openai(messages, model)


def _count_tokens_openai(messages: list[dict[str, str]], model: str) -> int:
    """
    Count tokens for OpenAI models using tiktoken.
    
    Args:
        messages: List of message dicts with 'role' and 'content' keys
        model: OpenAI model name
    
    Returns:
        Estimated token count
    """
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        encoding = tiktoken.get_encoding("cl100k_base")
    
    num_tokens = 0
    for message in messages:

        role = message.get("role", "")
        content = message.get("content", "")
        message_text = f"{role}{content}"
        num_tokens += len(encoding.encode(message_text))
        
       
        num_tokens += 3 
    
    num_tokens += 3 
    return num_tokens


def _count_tokens_gemini(messages: list[dict[str, str]], model: str) -> int:
    """
    Count tokens for Gemini models.
    
    Since Gemini uses a different tokenizer, we approximate using tiktoken's
    cl100k_base encoding as a rough estimate. This is not perfect but provides
    a reasonable approximation for context management.
    
    Args:
        messages: List of message dicts with 'role' and 'content' keys
        model: Gemini model name
    
    Returns:
        Estimated token count
    """
    encoding = tiktoken.get_encoding("cl100k_base")
    
    num_tokens = 0
    for message in messages:
        role = message.get("role", "")
        content = message.get("content", "")
        message_text = f"{role}{content}"
        num_tokens += len(encoding.encode(message_text))
        
        num_tokens += 3
    
    num_tokens += 3
    return num_tokens
