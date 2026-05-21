"""Task REST endpoints."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.task import Task
from ..schemas.task import TaskCreate, TaskOut, TaskUpdate
from ..utils.ids import make_id, now_iso

router = APIRouter(prefix="/tasks", tags=["任务管理"])


@router.get("", response_model=list[TaskOut], summary="任务列表", description="查询待办任务，可按会议、责任人、部门、状态和缺失信息筛选。")
def list_tasks(
    meeting_id: str | None = Query(default=None, description="会议 ID"),
    owner_name: str | None = Query(default=None, description="责任人姓名"),
    department_id: str | None = Query(default=None, description="部门 ID"),
    status: str | None = Query(default=None, description="任务状态：todo、doing、done、delayed"),
    missing_owner: bool | None = Query(default=None, description="是否只返回缺少责任人的任务"),
    missing_due: bool | None = Query(default=None, description="是否只返回缺少截止时间的任务"),
    db: Session = Depends(get_db),
):
    query = db.query(Task)
    if meeting_id is not None:
        query = query.filter(Task.meeting_id == meeting_id)
    if owner_name is not None:
        query = query.filter(Task.owner_name == owner_name)
    if department_id is not None:
        query = query.filter(Task.department_id == department_id)
    if status is not None:
        query = query.filter(Task.status == status)
    if missing_owner:
        query = query.filter((Task.owner_name == "") | (Task.owner_name.is_(None)))
    if missing_due:
        query = query.filter((Task.due_date == "") | (Task.due_date.is_(None)))
    return query.order_by(Task.created_at.desc()).all()


@router.post("", response_model=TaskOut, summary="创建任务", description="手动创建一条待办任务。AI 生成会议纪要时也会自动创建任务。")
def create_task(payload: TaskCreate, db: Session = Depends(get_db)):
    now = now_iso()
    task = Task(
        id=make_id("task"),
        meeting_id=payload.meeting_id,
        department_id=payload.department_id or "",
        owner_name=payload.owner_name or "",
        title=payload.title.strip(),
        due_date=payload.due_date or "",
        status=payload.status or "todo",
        created_at=now,
        updated_at=now,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@router.put("/{task_id}", response_model=TaskOut, summary="更新任务", description="更新任务标题、责任人、截止时间、部门、会议或状态。")
def update_task(task_id: str, payload: TaskUpdate, db: Session = Depends(get_db)):
    task = db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    data = payload.model_dump(exclude_unset=True)
    for field, value in data.items():
        if value is None and field in {"title"}:
            continue
        if value is None:
            continue
        setattr(task, field, value)
    task.updated_at = now_iso()
    db.commit()
    db.refresh(task)
    return task


@router.delete("/{task_id}", summary="删除任务", description="删除指定待办任务。")
def delete_task(task_id: str, db: Session = Depends(get_db)):
    task = db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    db.delete(task)
    db.commit()
    return {"detail": "已删除"}
