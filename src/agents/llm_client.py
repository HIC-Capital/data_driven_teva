"""
Shared LLM client — NVIDIA NIM (OpenAI-compatible API).
All agents import `chat()` from here instead of calling Anthropic directly.

Model: meta/llama-3.3-70b-instruct (best available on NVIDIA NIM)
Fallback: nvidia/llama-3.1-nemotron-70b-instruct
"""
from __future__ import annotations
import os

NVIDIA_BASE_URL = "https://integrate.api.nvidia.com/v1"
DEFAULT_MODEL   = "meta/llama-3.3-70b-instruct"


def _get_client():
    from openai import OpenAI
    api_key = os.environ.get("NVIDIA_API_KEY") or os.environ.get("NIM_API_KEY")
    if not api_key:
        raise RuntimeError(
            "No NVIDIA API key found. Set NVIDIA_API_KEY in .streamlit/secrets.toml"
        )
    return OpenAI(base_url=NVIDIA_BASE_URL, api_key=api_key)


def chat(
    messages: list[dict],
    system: str | None = None,
    model: str = DEFAULT_MODEL,
    max_tokens: int = 1024,
    temperature: float = 0.6,
) -> str:
    """
    Send a chat request to NVIDIA NIM. Returns the response text.

    Args:
        messages: list of {"role": "user"/"assistant", "content": "..."}
        system:   optional system prompt (prepended automatically)
        model:    NIM model ID (default: llama-3.3-70b-instruct)
        max_tokens: max output tokens
        temperature: 0=deterministic, 1=creative
    """
    client = _get_client()

    full_messages = []
    if system:
        full_messages.append({"role": "system", "content": system})
    full_messages.extend(messages)

    resp = client.chat.completions.create(
        model=model,
        messages=full_messages,
        max_tokens=max_tokens,
        temperature=temperature,
    )
    return resp.choices[0].message.content.strip()
