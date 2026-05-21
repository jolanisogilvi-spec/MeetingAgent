"""Meeting REST endpoints, including the AI minute-generation workflow."""
from __future__ import annotations

import shutil
import logging
from pathlib import Path
from urllib.parse import quote

from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, HTTPException, Query, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy import or_
from sqlalchemy.orm import Session

from ..config import KB_UPLOAD_EXTS, MAX_UPLOAD_SIZE, MEETING_UPLOAD_EXTS, UPLOAD_DIR
from ..database import SessionLocal, get_db
from ..models.meeting import Meeting
from ..models.settings import Settings
from ..models.task import Task
from ..schemas.meeting import MeetingCreate, MeetingOut, MeetingUpdate
from ..services import exporter, meeting_ai
from ..utils.ids import make_id, now_iso

router = APIRouter(prefix="/meetings", tags=["会议管理"])
logger = logging.getLogger(__name__)


@router.get("", response_model=list[MeetingOut], summary="会议列表", description="查询会议列表，可按状态、部门和关键词筛选。")
def list_meetings(
    status: str | None = Query(default=None, description="会议状态：draft、generating、completed、confirmed、failed"),
    department_id: str | None = Query(default=None, description="所属部门 ID"),
    keyword: str | None = Query(default=None, description="关键词；匹配会议名称、目标或备注"),
    db: Session = Depends(get_db),
):
    query = db.query(Meeting)
    if status:
        query = query.filter(Meeting.status == status)
    if department_id:
        query = query.filter(Meeting.department_id == department_id)
    if keyword:
        like = f"%{keyword}%"
        query = query.filter(
            or_(
                Meeting.title.ilike(like),
                Meeting.objective.ilike(like),
                Meeting.notes.ilike(like),
            )
        )
    return query.order_by(Meeting.updated_at.desc()).all()


@router.post("", response_model=MeetingOut, summary="创建会议", description="创建会议基础信息，初始状态为草稿。")
def create_meeting(payload: MeetingCreate, db: Session = Depends(get_db)):
    now = now_iso()
    meeting = Meeting(
        id=make_id("meeting"),
        title=payload.title.strip(),
        meeting_time=payload.meeting_time,
        department_id=payload.department_id,
        participant_ids=list(payload.participant_ids or []),
        meeting_type=payload.meeting_type,
        objective=payload.objective,
        notes=payload.notes,
        raw_text=payload.raw_text,
        status="draft",
        summary="",
        meeting_json={},
        error_message="",
        audio_filename="",
        kb_filenames=[],
        created_at=now,
        updated_at=now,
    )
    db.add(meeting)
    db.commit()
    db.refresh(meeting)
    return meeting


@router.get("/{meeting_id}", response_model=MeetingOut, summary="会议详情", description="根据会议 ID 查询会议详情。")
def get_meeting(meeting_id: str, db: Session = Depends(get_db)):
    meeting = db.get(Meeting, meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="会议不存在")
    return meeting


@router.put("/{meeting_id}", response_model=MeetingOut, summary="更新会议", description="更新会议基础信息、状态、原文、摘要或结构化纪要。保存 meeting_json 时会同步重建该会议的待办任务。")
def update_meeting(
    meeting_id: str, payload: MeetingUpdate, db: Session = Depends(get_db)
):
    meeting = db.get(Meeting, meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="会议不存在")
    data = payload.model_dump(exclude_unset=True)
    for field, value in data.items():
        if value is None and field in {"title"}:
            continue
        setattr(meeting, field, value)
    if "meeting_json" in data and isinstance(meeting.meeting_json, dict):
        meeting_ai.sync_tasks_from_json(db, meeting, meeting.meeting_json)
    meeting.updated_at = now_iso()
    db.commit()
    db.refresh(meeting)
    return meeting


@router.delete("/{meeting_id}", summary="删除会议", description="删除会议、关联待办任务和该会议上传目录。")
def delete_meeting(meeting_id: str, db: Session = Depends(get_db)):
    meeting = db.get(Meeting, meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="会议不存在")
    db.query(Task).filter(Task.meeting_id == meeting_id).delete(synchronize_session=False)
    upload_dir = UPLOAD_DIR / meeting_id
    if upload_dir.exists():
        shutil.rmtree(upload_dir, ignore_errors=True)
    db.delete(meeting)
    db.commit()
    return {"detail": "已删除"}


@router.post(
    "/{meeting_id}/generate",
    response_model=MeetingOut,
    summary="生成会议纪要",
    description=(
        "上传或提交会议材料，接口会先将会议标记为 generating 并立即返回，随后在后台执行 AI 纪要生成流程。"
        "支持粘贴文本、上传 mp3/wav/txt/docx 会议材料，以及上传 txt/docx 知识库参考资料。"
        "生成完成后会写回原文、摘要、结构化 JSON，并从 ActionItems 自动创建待办任务；前端可轮询会议详情查看状态。"
    ),
)
async def generate_meeting(
    meeting_id: str,
    background_tasks: BackgroundTasks,
    meeting_text: str = Form(default="", description="会议原文；若同时上传文件，则优先使用该文本"),
    meeting_file: UploadFile | None = File(default=None, description="会议文件，支持 .mp3、.wav、.txt、.docx，单文件最大 50MB"),
    kb_files: list[UploadFile] | None = File(default=None, description="知识库参考资料，支持多个 .txt 或 .docx 文件"),
    db: Session = Depends(get_db),
):
    meeting = db.get(Meeting, meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="会议不存在")

    settings = db.get(Settings, 1)
    if settings is None or not settings.llm_api_key or not settings.llm_model_name:
        raise HTTPException(status_code=400, detail="尚未配置大模型，请先在设置页保存")

    upload_dir = UPLOAD_DIR / meeting_id
    upload_dir.mkdir(parents=True, exist_ok=True)

    try:
        meeting_file_path = await _save_upload(meeting_file, upload_dir, MEETING_UPLOAD_EXTS)
    except HTTPException:
        raise
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=400, detail=f"会议文件保存失败：{exc}") from exc

    kb_paths: list[Path] = []
    kb_filenames: list[str] = []
    try:
        for kb in kb_files or []:
            saved = await _save_upload(kb, upload_dir, KB_UPLOAD_EXTS)
            if saved is not None:
                kb_paths.append(saved)
                kb_filenames.append(saved.name)
    except HTTPException:
        raise
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=400, detail=f"知识库文件保存失败：{exc}") from exc

    if meeting_file_path is not None:
        meeting.audio_filename = meeting_file_path.name
    if kb_filenames:
        meeting.kb_filenames = kb_filenames

    meeting.status = "generating"
    meeting.error_message = ""
    meeting.updated_at = now_iso()
    db.commit()
    db.refresh(meeting)
    background_tasks.add_task(
        _run_generation_job,
        meeting_id,
        meeting_text or "",
        str(meeting_file_path) if meeting_file_path else None,
        [str(p) for p in kb_paths],
    )
    return meeting


def _run_generation_job(
    meeting_id: str,
    meeting_text: str,
    meeting_file_path: str | None,
    kb_file_paths: list[str],
) -> None:
    db = SessionLocal()
    try:
        logger.info("meeting generation started: %s", meeting_id)
        meeting = db.get(Meeting, meeting_id)
        settings = db.get(Settings, 1)
        if meeting is None:
            logger.warning("meeting generation skipped, meeting not found: %s", meeting_id)
            return
        if settings is None:
            raise ValueError("尚未配置系统设置")
        meeting_ai.generate_minutes(
            db,
            meeting,
            settings,
            meeting_text=meeting_text,
            meeting_file_path=meeting_file_path,
            kb_file_paths=kb_file_paths,
        )
        logger.info("meeting generation finished: %s", meeting_id)
    except Exception as exc:  # noqa: BLE001
        logger.exception("meeting generation failed: %s", meeting_id)
        db.rollback()
        fresh = db.get(Meeting, meeting_id)
        if fresh is not None:
            fresh.status = "failed"
            fresh.error_message = str(exc)[:1000]
            fresh.updated_at = now_iso()
            db.commit()
    finally:
        db.close()


async def _save_upload(
    upload: UploadFile | None,
    directory: Path,
    allowed_exts: set[str],
) -> Path | None:
    """Validate type and size, then write the upload to `directory`."""
    if upload is None or not (upload.filename or "").strip():
        return None
    name = Path(upload.filename).name
    suffix = Path(name).suffix.lower()
    if suffix not in allowed_exts:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件类型 {suffix}，允许：{', '.join(sorted(allowed_exts))}",
        )
    target = directory / name
    written = 0
    with target.open("wb") as out:
        while True:
            chunk = await upload.read(1024 * 1024)
            if not chunk:
                break
            written += len(chunk)
            if written > MAX_UPLOAD_SIZE:
                out.close()
                target.unlink(missing_ok=True)
                raise HTTPException(status_code=400, detail="文件超过 50MB 限制")
            out.write(chunk)
    await upload.close()
    return target


@router.post("/{meeting_id}/export", summary="导出 Word 纪要", description="将已生成的会议摘要和结构化纪要导出为 .docx 文件。")
def export_meeting(meeting_id: str, db: Session = Depends(get_db)):
    meeting = db.get(Meeting, meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="会议不存在")
    if not (meeting.summary or "").strip() or not meeting.meeting_json:
        raise HTTPException(status_code=400, detail="请先生成会议纪要")

    try:
        target = exporter.export_meeting_to_docx(meeting, db)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=f"导出失败：{exc}") from exc

    encoded = quote(target.name)
    ascii_stem = Path(target.name).stem.encode("ascii", "ignore").decode("ascii").strip()
    ascii_fallback = f"{ascii_stem}.docx" if ascii_stem else f"{meeting_id}.docx"
    headers = {
        "Content-Disposition": (
            f"attachment; filename=\"{ascii_fallback}\"; filename*=UTF-8''{encoded}"
        )
    }
    return FileResponse(
        path=str(target),
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers=headers,
    )
