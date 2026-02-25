from typing import Dict, List, Optional
from app.services.llm import count_tokens, get_model_info


def build_context(
    messages: List[Dict[str, str]],
    system_prompt: Optional[str] = None,
    model: Optional[str] = None,
    max_context_ratio: float = 0.75,
) -> List[Dict[str, str]]:
    """
    Build a context window that fits within the model's token limit.

    - System prompt is always kept
    - Most recent messages are prioritized
    - Older messages are dropped first
    - max_context_ratio reserves space for the response (default 75% for input)
    """
    model_info = get_model_info(model)
    max_input = model_info.get("max_input_tokens") or model_info.get("max_tokens") or 8192
    token_budget = int(max_input * max_context_ratio)

    context = []
    used_tokens = 0

    # System prompt always goes first
    if system_prompt:
        system_msg = {"role": "system", "content": system_prompt}
        system_tokens = count_tokens([system_msg], model=model)
        context.append(system_msg)
        used_tokens += system_tokens
        token_budget -= system_tokens

    # Walk messages from newest to oldest
    reversed_messages = list(reversed(messages))
    kept = []

    for msg in reversed_messages:
        msg_tokens = count_tokens([msg], model=model)
        if used_tokens + msg_tokens > token_budget:
            break
        kept.append(msg)
        used_tokens += msg_tokens

    # Reverse back to chronological order
    kept.reverse()
    context.extend(kept)

    return context


def estimate_cost(
    prompt_tokens: int,
    completion_tokens: int,
    model: Optional[str] = None,
) -> Dict[str, float]:
    """Estimate the cost of a request."""
    model_info = get_model_info(model)
    input_cost = model_info.get("input_cost_per_token") or 0
    output_cost = model_info.get("output_cost_per_token") or 0

    return {
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": prompt_tokens + completion_tokens,
        "input_cost": prompt_tokens * input_cost,
        "output_cost": completion_tokens * output_cost,
        "total_cost": (prompt_tokens * input_cost) + (completion_tokens * output_cost),
    }
