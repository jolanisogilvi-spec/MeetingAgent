"""LLM client wrapper (OpenAI-compatible)."""
from __future__ import annotations

from typing import Any

from openai import OpenAI


def build_client(api_key: str, base_url: str | None) -> OpenAI:
    if not api_key:
        raise ValueError("缺少 API Key")
    kwargs: dict[str, Any] = {"api_key": api_key, "timeout": 30.0}
    if base_url:
        kwargs["base_url"] = base_url.rstrip("/")
    return OpenAI(**kwargs)


def chat(
    *,
    api_key: str,
    base_url: str | None,
    model: str,
    messages: list[dict],
    temperature: float = 0.3,
    max_tokens: int = 1024,
    response_format: dict | None = None,
    timeout: float = 60.0,
) -> str:
    """Generic chat completion, returns assistant content string."""
    if not model:
        raise ValueError("缺少模型名称")
    client = build_client(api_key, base_url)
    kwargs: dict[str, Any] = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "timeout": timeout,
    }
    if response_format is not None:
        kwargs["response_format"] = response_format
    resp = client.chat.completions.create(**kwargs)
    return (resp.choices[0].message.content or "").strip()


def test_llm(
    *,
    api_key: str,
    base_url: str | None,
    model: str,
    temperature: float = 0.3,
    max_tokens: int = 32,
) -> dict:
    """Return {ok, message, extra} for a quick ping test."""
    try:
        content = chat(
            api_key=api_key,
            base_url=base_url,
            model=model,
            messages=[
                {"role": "system", "content": "你是测试助手，请简短回复。"},
                {"role": "user", "content": "请回复 ok"},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=15.0,
        )
        return {"ok": True, "message": "测试成功", "extra": {"reply": content}}
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "message": f"测试失败：{exc}"}
