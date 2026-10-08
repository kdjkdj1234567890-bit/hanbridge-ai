"""Thin client for Nebius Token Factory (OpenAI-compatible API).

Docs: https://docs.tokenfactory.nebius.com
Base URL: https://api.tokenfactory.nebius.com/v1/
"""

from __future__ import annotations

import json
import re

from openai import OpenAI

from . import config


class MissingApiKeyError(RuntimeError):
    """Raised when no Nebius Token Factory API key is configured."""


def get_client(api_key: str | None = None) -> OpenAI:
    """Return an OpenAI-compatible client pointed at Nebius Token Factory."""
    key = (api_key or config.NEBIUS_API_KEY).strip()
    if not key:
        raise MissingApiKeyError(
            "NEBIUS_API_KEY is not set. Get a free key at "
            "https://tokenfactory.nebius.com/ and set it as an environment "
            "variable (or paste it in the app sidebar)."
        )
    return OpenAI(base_url=config.NEBIUS_BASE_URL, api_key=key)


def list_models(api_key: str | None = None) -> list[str]:
    """List model IDs available to this key via the /v1/models endpoint."""
    client = get_client(api_key)
    resp = client.models.list()
    return sorted(m.id for m in resp.data)


def pick_nvidia_model(model_ids: list[str]) -> str:
    """Prefer an NVIDIA/Nemotron model; fall back to the first available."""
    lowered = [(m, m.lower()) for m in model_ids]
    for hint in config.NVIDIA_HINTS:
        for original, low in lowered:
            if hint in low:
                return original
    return model_ids[0] if model_ids else ""


def extract_json(text: str) -> dict:
    """Robustly extract a JSON object from model output (fences tolerated)."""
    text = text.strip()
    fence = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
    if fence:
        text = fence.group(1).strip()
    start, end = text.find("{"), text.rfind("}")
    if start != -1 and end != -1 and end > start:
        text = text[start : end + 1]
    return json.loads(text)


def translate_json(
    client: OpenAI,
    model: str,
    system_prompt: str,
    user_text: str,
    temperature: float = 0.3,
    max_tokens: int = 1500,
) -> dict:
    """Ask the model for a translation + coaching notes, returned as a dict."""
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_text},
        ],
        temperature=temperature,
        max_tokens=max_tokens,
        response_format={"type": "json_object"},
    )
    return extract_json(resp.choices[0].message.content or "{}")


def translate_text(
    client: OpenAI,
    model: str,
    system_prompt: str,
    user_text: str,
    temperature: float = 0.3,
    max_tokens: int = 800,
) -> str:
    """Plain-text translation (used for fast chat messages)."""
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_text},
        ],
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return (resp.choices[0].message.content or "").strip()
