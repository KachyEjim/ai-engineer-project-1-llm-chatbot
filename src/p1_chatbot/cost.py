"""
Cost estimation utilities for chatbot API usage.
"""
from typing import Dict, Tuple


MODEL_PRICING_USD_PER_1K: Dict[str, Tuple[float, float]] = {
    "gpt-4o-mini": (0.0005, 0.0015),
    "gemini-2.5-flash-lite": (0.00025, 0.0005),
}

def estimate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    """
    Estimate the USD cost for a model call.
    Args:
        model: Model name (str)
        input_tokens: Number of prompt tokens (int)
        output_tokens: Number of completion tokens (int)
    Returns:
        Estimated cost in USD (float)
    Raises:
        ValueError: If model is not in MODEL_PRICING_USD_PER_1K
    """
    if model not in MODEL_PRICING_USD_PER_1K:
        raise ValueError(f"Model '{model}' not found in pricing table.")
    input_per_1k, output_per_1k = MODEL_PRICING_USD_PER_1K[model]
    return (input_tokens / 1000) * input_per_1k + (output_tokens / 1000) * output_per_1k
