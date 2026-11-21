"""Optional OpenRouter call. The default path never reaches this module's network code.

If the provider times out, rate-limits, or is not configured, the caller keeps
the extractive draft. That is acceptance criterion A11.
"""

from __future__ import annotations

import time

import requests

from src.config import get_settings


class ProviderError(RuntimeError):
    """The model provider could not return a usable completion."""


def complete(system_prompt: str, user_prompt: str) -> str:
    settings = get_settings()
    key = (settings.api_key or "").strip()
    if not settings.use_llm or not key or key == "your_key_here":
        raise ProviderError("Model provider is not configured.")
    delay = 1.0
    last_error = "no response"
    for _attempt in range(3):
        try:
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={"Authorization": f"Bearer {key}"},
                json={
                    "model": settings.model_name,
                    "temperature": 0,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                },
                timeout=20,
            )
        except requests.RequestException as exc:
            raise ProviderError(f"Model provider request failed: {exc}") from exc
        if response.status_code == 429:
            last_error = "rate limited"
            time.sleep(delay)
            delay *= 2
            continue
        if response.status_code >= 500:
            last_error = f"provider status {response.status_code}"
            time.sleep(delay)
            continue
        if response.status_code != 200:
            raise ProviderError(f"Model provider returned status {response.status_code}.")
        try:
            return response.json()["choices"][0]["message"]["content"]
        except (KeyError, IndexError, ValueError, TypeError) as exc:
            raise ProviderError("Model provider returned an unexpected payload.") from exc
    raise ProviderError(f"Model provider unavailable after retries ({last_error}).")
