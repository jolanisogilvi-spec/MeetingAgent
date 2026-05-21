"""Embedding client wrapper (OpenAI-compatible)."""
from __future__ import annotations

from typing import Any

from openai import OpenAI


def normalize_base_url(base_url: str | None) -> str | None:
    """Strip a trailing /embeddings so openai SDK gets the /v1 root."""
    if not base_url:
        return base_url
    url = base_url.rstrip("/")
    if url.endswith("/embeddings"):
        url = url[: -len("/embeddings")]
    return url


def build_client(api_key: str, base_url: str | None) -> OpenAI:
    if not api_key:
        raise ValueError("缺少 API Key")
    kwargs: dict[str, Any] = {"api_key": api_key, "timeout": 30.0}
    normalized = normalize_base_url(base_url)
    if normalized:
        kwargs["base_url"] = normalized
    return OpenAI(**kwargs)


def embed(
    *,
    api_key: str,
    base_url: str | None,
    model: str,
    texts: list[str],
    timeout: float = 60.0,
) -> list[list[float]]:
    if not model:
        raise ValueError("缺少 embedding 模型名称")
    if not texts:
        return []
    client = build_client(api_key, base_url)
    resp = client.embeddings.create(model=model, input=texts, timeout=timeout)
    return [item.embedding for item in resp.data]


def test_embedding(
    *,
    api_key: str,
    base_url: str | None,
    model: str,
) -> dict:
    try:
        vectors = embed(
            api_key=api_key,
            base_url=base_url,
            model=model,
            texts=["ping"],
            timeout=15.0,
        )
        dim = len(vectors[0]) if vectors else 0
        return {"ok": True, "message": "测试成功", "extra": {"dim": dim}}
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "message": f"测试失败：{exc}"}
