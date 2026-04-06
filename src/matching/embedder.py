"""
Embedding utilities for thesis matching.

Uses NVIDIA NIM embedding endpoint (nvidia/nv-embedqa-e5-v5).
Results are cached on disk so re-runs don't re-call the API for unchanged text.
"""

import hashlib
import json
import os

import numpy as np

_CACHE_PATH = "data/embeddings_cache.json"
_cache: dict[str, list[float]] = {}
_cache_loaded = False
_cache_dirty = False

NIM_EMBED_MODEL = "nvidia/nv-embedqa-e5-v5"
NVIDIA_BASE_URL = "https://integrate.api.nvidia.com/v1"


def _get_client():
    from openai import OpenAI
    api_key = os.environ.get("NVIDIA_API_KEY") or os.environ.get("NIM_API_KEY")
    if not api_key:
        raise RuntimeError("No NVIDIA API key found. Set NVIDIA_API_KEY in .streamlit/secrets.toml")
    return OpenAI(base_url=NVIDIA_BASE_URL, api_key=api_key)


def _load_cache() -> None:
    global _cache, _cache_loaded
    if _cache_loaded:
        return
    if os.path.exists(_CACHE_PATH):
        with open(_CACHE_PATH, encoding="utf-8") as f:
            _cache = json.load(f)
    _cache_loaded = True


def flush_cache() -> None:
    """Write cache to disk. Called after batch operations."""
    global _cache_dirty
    if not _cache_dirty:
        return
    os.makedirs("data", exist_ok=True)
    with open(_CACHE_PATH, "w", encoding="utf-8") as f:
        json.dump(_cache, f)
    _cache_dirty = False


def _key(text: str) -> str:
    return hashlib.md5(text.encode()).hexdigest()


def embed_text(text: str, client=None) -> list[float]:
    """Embed a single text string. Caches by content hash."""
    global _cache_dirty
    _load_cache()

    safe = text.strip() or "N/A"
    k = _key(safe)
    if k in _cache:
        return _cache[k]

    if client is None:
        client = _get_client()

    response = client.embeddings.create(
        model=NIM_EMBED_MODEL, input=[safe],
        extra_body={"input_type": "query", "truncate": "END"},
    )
    vec = response.data[0].embedding
    _cache[k] = vec
    _cache_dirty = True
    flush_cache()
    return vec


def embed_batch(texts: list[str], client=None) -> list[list[float]]:
    """
    Embed a list of texts. Only calls the API for uncached entries.
    Returns vectors in the same order as the input list.
    """
    global _cache_dirty
    _load_cache()

    if client is None:
        client = _get_client()

    results: list[list[float] | None] = [None] * len(texts)
    missing_indices: list[int] = []
    missing_texts: list[str] = []

    for i, text in enumerate(texts):
        safe = text.strip() or "N/A"
        k = _key(safe)
        if k in _cache:
            results[i] = _cache[k]
        else:
            missing_indices.append(i)
            missing_texts.append(safe)

    if missing_texts:
        # NIM embedding endpoint: batch in chunks of 96 (safe limit)
        CHUNK = 96
        api_vecs: list[list[float]] = []
        for start in range(0, len(missing_texts), CHUNK):
            chunk = missing_texts[start : start + CHUNK]
            resp = client.embeddings.create(
                model=NIM_EMBED_MODEL, input=chunk,
                extra_body={"input_type": "passage", "truncate": "END"},
            )
            resp.data.sort(key=lambda x: x.index)
            api_vecs.extend(item.embedding for item in resp.data)

        for j, idx in enumerate(missing_indices):
            k = _key(missing_texts[j])
            _cache[k] = api_vecs[j]
            results[idx] = api_vecs[j]
        _cache_dirty = True

    flush_cache()
    return results  # type: ignore[return-value]


def cosine_similarity(a: list[float], b: list[float]) -> float:
    """Cosine similarity in [−1, 1]. Returns 0 for zero vectors."""
    va = np.array(a, dtype=np.float32)
    vb = np.array(b, dtype=np.float32)
    denom = np.linalg.norm(va) * np.linalg.norm(vb)
    if denom < 1e-10:
        return 0.0
    return float(np.dot(va, vb) / denom)
