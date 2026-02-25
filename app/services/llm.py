from typing import Any, Dict, List, Optional, Generator
import litellm
from app.core.config import settings

# Suppress LiteLLM debug logs
litellm.set_verbose = False


def chat_completion(
    messages: List[Dict[str, str]],
    model: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: Optional[int] = None,
    stream: bool = False,
    **kwargs,
) -> Any:
    """Send a chat completion request through LiteLLM."""
    model = model or settings.DEFAULT_MODEL

    params = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "stream": stream,
        **kwargs,
    }

    if max_tokens:
        params["max_tokens"] = max_tokens

    response = litellm.completion(**params)
    return response


def chat_completion_stream(
    messages: List[Dict[str, str]],
    model: Optional[str] = None,
    temperature: float = 1.0,
    max_tokens: Optional[int] = None,
    **kwargs,
) -> Generator:
    """Stream a chat completion response."""
    model = model or settings.DEFAULT_MODEL

    response = litellm.completion(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
        stream=True,
        **kwargs,
    )

    for chunk in response:
        delta = chunk.choices[0].delta
        if delta.content:
            yield delta.content


def count_tokens(messages: List[Dict[str, str]], model: Optional[str] = None) -> int:
    """Count tokens for a list of messages."""
    model = model or settings.DEFAULT_MODEL
    return litellm.token_counter(model=model, messages=messages)


def get_model_info(model: Optional[str] = None) -> Dict[str, Any]:
    """Get model metadata (context window, costs, etc.)."""
    model = model or settings.DEFAULT_MODEL
    try:
        info = litellm.get_model_info(model)
        return {
            "model": model,
            "max_tokens": info.get("max_tokens"),
            "max_input_tokens": info.get("max_input_tokens"),
            "max_output_tokens": info.get("max_output_tokens"),
            "input_cost_per_token": info.get("input_cost_per_token"),
            "output_cost_per_token": info.get("output_cost_per_token"),
        }
    except Exception:
        return {"model": model, "error": "Model info not available"}
