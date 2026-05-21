"""AI workflow for meeting minute generation.

Three sequential LLM steps:
  1. summary  — Chinese summary of the meeting.
  2. extract  — Structured JSON (Topic / KeyPoints / Decisions / ActionItems).
  3. review   — JSON quality-check and completion pass.

The structured JSON drives task creation. All LLM calls go through
`services.llm.chat()`. JSON parsing has a single retry; a hard ValueError is
raised after two failures so the API layer marks the meeting as failed.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from sqlalchemy.orm import Session

from ..config import UPLOAD_DIR
from ..models.meeting import Meeting
from ..models.settings import Settings
from ..models.task import Task
from ..utils.ids import make_id, now_iso
from . import llm as llm_service
from . import rag as rag_service
from . import speech as speech_service
from .file_parser import parse_file

MEETING_TEXT_BUDGET = 8000
JSON_SCHEMA_HINT = (
    '{"Topic": "", "KeyPoints": [], "Decisions": [], '
    '"ActionItems": [{"Who": "", "What": "", "When": ""}]}'
)


def generate_minutes(
    db: Session,
    meeting: Meeting,
    settings: Settings,
    *,
    meeting_text: str = "",
    meeting_file_path: str | Path | None = None,
    kb_file_paths: list[str | Path] | None = None,
) -> Meeting:
    """Run the full workflow and persist results onto the Meeting row.

    Caller is responsible for setting status=generating before calling, and
    for catching exceptions to mark status=failed with error_message.
    """
    if not settings.llm_api_key or not settings.llm_model_name:
        raise ValueError("尚未配置大模型，请先在设置页保存大模型 API Key 与模型名称")

    raw_text = _prepare_raw_text(
        meeting=meeting,
        settings=settings,
        meeting_text=meeting_text,
        meeting_file_path=meeting_file_path,
    )
    if not raw_text.strip():
        raise ValueError("会议内容为空，请粘贴会议文本或上传会议文件")

    kb_context = _build_kb_context(
        settings=settings,
        kb_file_paths=kb_file_paths or [],
        query=raw_text,
    )

    truncated_text = raw_text[:MEETING_TEXT_BUDGET]

    summary = _step_summary(settings, truncated_text, kb_context)
    extracted = _step_extract(settings, truncated_text, kb_context)
    reviewed = _step_review(settings, truncated_text, summary, extracted, kb_context)
    final_json = _normalize_meeting_json(reviewed)

    meeting.raw_text = raw_text
    meeting.summary = summary
    meeting.meeting_json = final_json
    meeting.status = "completed"
    meeting.error_message = ""
    meeting.updated_at = now_iso()

    sync_tasks_from_json(db, meeting, final_json)

    db.commit()
    db.refresh(meeting)
    return meeting


def _prepare_raw_text(
    *,
    meeting: Meeting,
    settings: Settings,
    meeting_text: str,
    meeting_file_path: str | Path | None,
) -> str:
    text = (meeting_text or "").strip()
    if text:
        return text

    if meeting_file_path:
        p = Path(meeting_file_path)
        suffix = p.suffix.lower()
        if suffix in {".mp3", ".wav"}:
            transcript = speech_service.transcribe(
                str(p),
                provider=settings.speech_provider or "local",
                api_key=settings.speech_api_key or "",
                base_url=settings.speech_base_url or "",
                model_name=settings.speech_model_name or "",
                model_type=settings.speech_model_type or "",
            )
            return (transcript or "").strip()
        if suffix in {".txt", ".docx"}:
            return parse_file(p).strip()
        raise ValueError(f"不支持的会议文件类型：{suffix}")

    return (meeting.raw_text or "").strip()


def _build_kb_context(
    *,
    settings: Settings,
    kb_file_paths: list[str | Path],
    query: str,
) -> str:
    if not kb_file_paths:
        return ""
    if not settings.embedding_api_key or not settings.embedding_model_name:
        return ""
    try:
        index = rag_service.build_index(
            kb_file_paths,
            api_key=settings.embedding_api_key,
            base_url=settings.embedding_base_url or None,
            model=settings.embedding_model_name,
        )
        if index.empty:
            return ""
        snippets = rag_service.retrieve(
            index,
            query,
            api_key=settings.embedding_api_key,
            base_url=settings.embedding_base_url or None,
            model=settings.embedding_model_name,
            top_k=5,
        )
        return rag_service.format_context(snippets)
    except Exception:
        # RAG is best-effort — never block minute generation if it fails.
        return ""


def _step_summary(settings: Settings, raw_text: str, kb_context: str) -> str:
    system = (
        "你是一名资深会议秘书，擅长用中文撰写企业内部会议摘要。"
        "请输出 200-400 字的中文摘要，覆盖核心议题、关键讨论、结论与待办；"
        "不要使用 markdown 标题或列表符号，只输出纯文本。"
    )
    user = _compose_user_message(
        instruction="请基于下面的会议原文撰写中文摘要。",
        raw_text=raw_text,
        kb_context=kb_context,
    )
    content = llm_service.chat(
        api_key=settings.llm_api_key,
        base_url=settings.llm_base_url or None,
        model=settings.llm_model_name,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        temperature=float(settings.temperature or 0.3),
        max_tokens=int(settings.max_tokens or 1024),
    )
    return content.strip()


def _step_extract(settings: Settings, raw_text: str, kb_context: str) -> dict[str, Any]:
    system = (
        "你是一名会议纪要结构化助手。请阅读会议原文，抽取以下结构化 JSON："
        f"\n{JSON_SCHEMA_HINT}\n"
        "要求：字段不可缺失；没有内容时使用空字符串或空数组；"
        "ActionItems 中每一项需包含 Who、What、When 三个字段；"
        "只输出 JSON 对象本身，不要包含 markdown 代码块、解释文字或多余字段；"
        "所有内容必须使用中文。"
    )
    user = _compose_user_message(
        instruction="请抽取会议结构化纪要 JSON。",
        raw_text=raw_text,
        kb_context=kb_context,
    )
    return _chat_json(
        settings=settings,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    )


def _step_review(
    settings: Settings,
    raw_text: str,
    summary: str,
    extracted: dict[str, Any],
    kb_context: str,
) -> dict[str, Any]:
    system = (
        "你是一名会议纪要质检员。请基于会议原文、摘要以及已抽取的 JSON，"
        "检查是否遗漏关键讨论点、决策结论或待办任务，并补全或修订。"
        "保持原有 JSON Schema 不变："
        f"\n{JSON_SCHEMA_HINT}\n"
        "要求：字段不可缺失；没有内容时使用空字符串或空数组；"
        "只输出最终 JSON 对象本身，不要包含 markdown 代码块或解释文字；"
        "所有内容必须使用中文。"
    )
    extracted_json = json.dumps(extracted, ensure_ascii=False)
    user_parts: list[str] = [
        "请审阅并补全下列会议结构化纪要 JSON。",
        f"【已抽取 JSON】\n{extracted_json}",
        f"【会议摘要】\n{summary}",
    ]
    if kb_context:
        user_parts.append(f"【知识库参考】\n{kb_context}")
    user_parts.append(f"【会议原文】\n{raw_text}")
    user = "\n\n".join(user_parts)

    return _chat_json(
        settings=settings,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    )


def _compose_user_message(*, instruction: str, raw_text: str, kb_context: str) -> str:
    parts = [instruction]
    if kb_context:
        parts.append(f"【知识库参考】\n{kb_context}")
    parts.append(f"【会议原文】\n{raw_text}")
    return "\n\n".join(parts)


def _chat_json(*, settings: Settings, messages: list[dict]) -> dict[str, Any]:
    """Call the LLM expecting a JSON object. Retries once on parse failure."""
    last_error: Exception | None = None
    for attempt in range(2):
        try:
            content = llm_service.chat(
                api_key=settings.llm_api_key,
                base_url=settings.llm_base_url or None,
                model=settings.llm_model_name,
                messages=messages,
                temperature=float(settings.temperature or 0.3),
                max_tokens=int(settings.max_tokens or 1024),
                response_format={"type": "json_object"},
            )
            return _parse_json_object(content)
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            if attempt == 0:
                messages = messages + [
                    {
                        "role": "user",
                        "content": "上一轮输出无法解析为 JSON，请只输出合法的 JSON 对象，不要 markdown 代码块。",
                    }
                ]
                continue
    raise ValueError(f"模型输出 JSON 解析失败：{last_error}")


def _parse_json_object(content: str) -> dict[str, Any]:
    if not content:
        raise ValueError("模型返回为空")
    text = content.strip()
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if not match:
            raise ValueError("模型返回内容不是 JSON")
        data = json.loads(match.group(0))
    if not isinstance(data, dict):
        raise ValueError("模型返回不是 JSON 对象")
    return data


def _normalize_meeting_json(data: dict[str, Any]) -> dict[str, Any]:
    """Coerce any partial structure into the canonical schema."""
    topic = data.get("Topic") or ""
    key_points = _ensure_str_list(data.get("KeyPoints"))
    decisions = _ensure_str_list(data.get("Decisions"))

    action_items: list[dict[str, str]] = []
    raw_items = data.get("ActionItems")
    if isinstance(raw_items, list):
        for item in raw_items:
            if isinstance(item, dict):
                action_items.append(
                    {
                        "Who": _as_str(item.get("Who")),
                        "What": _as_str(item.get("What")),
                        "When": _as_str(item.get("When")),
                    }
                )
            elif isinstance(item, str) and item.strip():
                action_items.append({"Who": "", "What": item.strip(), "When": ""})

    return {
        "Topic": _as_str(topic),
        "KeyPoints": key_points,
        "Decisions": decisions,
        "ActionItems": action_items,
    }


def _ensure_str_list(value: Any) -> list[str]:
    if not value:
        return []
    if isinstance(value, list):
        return [_as_str(v) for v in value if _as_str(v)]
    if isinstance(value, str):
        text = value.strip()
        return [text] if text else []
    return []


def _as_str(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    return str(value).strip()


def sync_tasks_from_json(db: Session, meeting: Meeting, data: dict[str, Any]) -> None:
    """Replace this meeting's auto-generated tasks with the current ActionItems."""
    db.query(Task).filter(Task.meeting_id == meeting.id).delete(synchronize_session=False)
    items = data.get("ActionItems") or []
    if not isinstance(items, list):
        return
    now = now_iso()
    for item in items:
        if not isinstance(item, dict):
            continue
        title = _as_str(item.get("What"))
        if not title:
            continue
        task = Task(
            id=make_id("task"),
            meeting_id=meeting.id,
            department_id=meeting.department_id or "",
            owner_name=_as_str(item.get("Who")),
            title=title,
            due_date=_as_str(item.get("When")),
            status="todo",
            created_at=now,
            updated_at=now,
        )
        db.add(task)
