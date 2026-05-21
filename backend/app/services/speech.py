"""Speech recognition: local faster-whisper or OpenAI-compatible online API."""
from __future__ import annotations

from typing import Any

import httpx


def transcribe_local(audio_path: str, model_name: str = "base") -> str:
    """Transcribe with faster-whisper. Raises if the package is missing."""
    try:
        from faster_whisper import WhisperModel  # type: ignore
    except Exception as exc:  # noqa: BLE001
        raise RuntimeError(f"未安装 faster-whisper：{exc}") from exc
    model = WhisperModel(model_name or "base")
    segments, _ = model.transcribe(audio_path)
    return "".join(seg.text for seg in segments).strip()


def transcribe_online(
    audio_path: str,
    *,
    api_key: str,
    base_url: str,
    model_name: str,
) -> str:
    """Transcribe via OpenAI-compatible /audio/transcriptions endpoint."""
    if not api_key:
        raise ValueError("缺少 API Key")
    if not base_url:
        raise ValueError("缺少 base_url")
    if not model_name:
        raise ValueError("缺少模型名称")
    url = base_url.rstrip("/")
    if not url.endswith("/audio/transcriptions"):
        if not url.endswith("/v1"):
            url = url.rstrip("/") + "/v1"
        url = url + "/audio/transcriptions"
    with open(audio_path, "rb") as f:
        files = {"file": (audio_path.rsplit("/", 1)[-1], f, "application/octet-stream")}
        data = {"model": model_name}
        headers = {"Authorization": f"Bearer {api_key}"}
        with httpx.Client(timeout=120.0) as client:
            resp = client.post(url, headers=headers, data=data, files=files)
            resp.raise_for_status()
            payload = resp.json()
    return (payload.get("text") or "").strip()


def transcribe(
    audio_path: str,
    *,
    provider: str,
    api_key: str,
    base_url: str,
    model_name: str,
) -> str:
    if provider == "online":
        return transcribe_online(
            audio_path, api_key=api_key, base_url=base_url, model_name=model_name
        )
    return transcribe_local(audio_path, model_name=model_name or "base")


def test_speech(
    *,
    provider: str,
    model_type: str = "",
    api_key: str = "",
    base_url: str = "",
    model_name: str = "",
) -> dict[str, Any]:
    if provider == "local":
        try:
            from faster_whisper import WhisperModel  # type: ignore
        except Exception as exc:  # noqa: BLE001
            return {"ok": False, "message": f"未安装 faster-whisper：{exc}"}
        try:
            WhisperModel(model_name or "base")
            return {
                "ok": True,
                "message": "本地模型加载成功",
                "extra": {"model": model_name or "base"},
            }
        except Exception as exc:  # noqa: BLE001
            return {"ok": False, "message": f"本地模型加载失败：{exc}"}

    if not base_url:
        return {"ok": False, "message": "缺少 base_url"}
    url = base_url.rstrip("/")
    headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
    try:
        with httpx.Client(timeout=10.0) as client:
            resp = client.get(url, headers=headers)
        ok = resp.status_code < 500
        return {
            "ok": ok,
            "message": f"已连接：HTTP {resp.status_code}" if ok else f"服务异常：HTTP {resp.status_code}",
            "extra": {"status": resp.status_code},
        }
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "message": f"连接失败：{exc}"}
