"""Speech recognition: local faster-whisper or OpenAI-compatible online API."""
from __future__ import annotations

import json
import math
import os
import tempfile
import wave
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
    model_type: str = "",
) -> str:
    """Transcribe via an OpenAI-compatible /audio/transcriptions endpoint."""
    if not api_key:
        raise ValueError("缺少 API Key")
    if not base_url:
        raise ValueError("缺少 Base URL")
    if not model_name:
        raise ValueError("缺少模型名称")

    url = _transcription_url(base_url)
    with open(audio_path, "rb") as f:
        files = {"file": (os.path.basename(audio_path), f, "audio/wav")}
        data = {"model": model_name}
        if _should_stream(base_url=base_url, model_name=model_name, model_type=model_type):
            data["stream"] = "true"
        headers = {"Authorization": f"Bearer {api_key}"}
        with httpx.Client(timeout=120.0) as client:
            resp = client.post(url, headers=headers, data=data, files=files)
            resp.raise_for_status()
            return _extract_transcript(resp).strip()


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
    audio_path = _create_test_wav()
    try:
        if provider == "local":
            return _test_local(audio_path, model_name=model_name)
        return _test_online(
            audio_path,
            api_key=api_key,
            base_url=base_url,
            model_name=model_name,
            model_type=model_type,
        )
    finally:
        try:
            os.remove(audio_path)
        except OSError:
            pass


def _test_local(audio_path: str, *, model_name: str = "") -> dict[str, Any]:
    try:
        transcript = transcribe_local(audio_path, model_name=model_name or "base")
        return {
            "ok": True,
            "message": "已完成一次本地测试音频转写",
            "extra": {
                "model": model_name or "base",
                "provider": "local",
                "transcript": transcript,
                "test_audio": "内置短音频",
            },
        }
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "message": f"本地测试音频转写失败：{exc}"}


def _test_online(
    audio_path: str,
    *,
    api_key: str = "",
    base_url: str = "",
    model_name: str = "",
    model_type: str = "",
) -> dict[str, Any]:
    if not api_key:
        return {"ok": False, "message": "缺少 API Key"}
    if not base_url:
        return {"ok": False, "message": "缺少 Base URL"}
    if not model_name:
        return {"ok": False, "message": "缺少模型名称"}

    try:
        transcript = transcribe_online(
            audio_path,
            api_key=api_key,
            base_url=base_url,
            model_name=model_name,
            model_type=model_type,
        )
        return {
            "ok": True,
            "message": "已完成一次线上测试音频转写",
            "extra": {
                "model": model_name,
                "model_type": model_type,
                "provider": "online",
                "transcript": transcript,
                "endpoint": _transcription_url(base_url),
                "stream": _should_stream(
                    base_url=base_url, model_name=model_name, model_type=model_type
                ),
                "test_audio": "内置短音频",
            },
        }
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "message": f"线上测试音频转写失败：{exc}"}


def _transcription_url(base_url: str) -> str:
    url = base_url.rstrip("/")
    if url.endswith("/audio/transcriptions"):
        return url
    if not url.endswith("/v1"):
        url = url + "/v1"
    return url + "/audio/transcriptions"


def _should_stream(*, base_url: str, model_name: str, model_type: str = "") -> bool:
    value = f"{base_url} {model_name} {model_type}".lower()
    return "bigmodel.cn" in value or "glm-asr" in value


def _create_test_wav() -> str:
    """Create a tiny WAV file that exercises the upload/transcription path."""
    fd, path = tempfile.mkstemp(prefix="meeting-agent-speech-test-", suffix=".wav")
    os.close(fd)

    sample_rate = 16000
    duration_seconds = 1.2
    total_samples = int(sample_rate * duration_seconds)
    amplitude = 9000

    with wave.open(path, "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        frames = bytearray()
        for index in range(total_samples):
            # A short two-tone signal is enough to validate multipart audio upload.
            t = index / sample_rate
            envelope = min(1.0, index / 800, (total_samples - index) / 800)
            value = int(
                amplitude
                * envelope
                * (
                    0.65 * math.sin(2 * math.pi * 440 * t)
                    + 0.35 * math.sin(2 * math.pi * 660 * t)
                )
            )
            frames.extend(value.to_bytes(2, byteorder="little", signed=True))
        wav.writeframes(bytes(frames))

    return path


def _extract_transcript(resp: httpx.Response) -> str:
    content_type = resp.headers.get("content-type", "").lower()
    if "application/json" in content_type:
        return _extract_text_from_payload(resp.json())

    text = resp.text.strip()
    if not text:
        return ""

    chunks: list[str] = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith("data:"):
            line = line[5:].strip()
        if line == "[DONE]":
            continue
        try:
            chunks.append(_extract_text_from_payload(json.loads(line)))
        except json.JSONDecodeError:
            chunks.append(line)
    return "".join(chunks).strip()


def _extract_text_from_payload(payload: Any) -> str:
    if isinstance(payload, str):
        return payload
    if not isinstance(payload, dict):
        return ""

    for key in ("text", "content", "transcript"):
        value = payload.get(key)
        if isinstance(value, str):
            return value

    result = payload.get("result") or payload.get("data")
    if isinstance(result, dict):
        nested = _extract_text_from_payload(result)
        if nested:
            return nested

    choices = payload.get("choices")
    if isinstance(choices, list):
        parts = []
        for choice in choices:
            if not isinstance(choice, dict):
                continue
            for key in ("text", "delta", "message"):
                value = choice.get(key)
                if isinstance(value, str):
                    parts.append(value)
                elif isinstance(value, dict):
                    nested = _extract_text_from_payload(value)
                    if nested:
                        parts.append(nested)
        return "".join(parts)

    return ""
