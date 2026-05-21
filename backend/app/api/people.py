"""Person REST endpoints."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.department import Department
from ..models.person import Person
from ..schemas.person import PersonCreate, PersonOut, PersonUpdate
from ..utils.ids import make_id, now_iso

router = APIRouter(prefix="/people", tags=["人员管理"])


def _ensure_department(db: Session, department_id: str | None) -> None:
    if department_id is None:
        return
    if not db.get(Department, department_id):
        raise HTTPException(status_code=400, detail="所属部门不存在")


@router.get("", response_model=list[PersonOut], summary="人员列表", description="查询人员列表，可按部门 ID 筛选。")
def list_people(
    department_id: str | None = Query(default=None, description="部门 ID；留空返回全部人员"),
    db: Session = Depends(get_db),
):
    query = db.query(Person)
    if department_id is not None:
        query = query.filter(Person.department_id == department_id)
    return query.order_by(Person.created_at.desc()).all()


@router.post("", response_model=PersonOut, summary="创建人员", description="创建人员资料，可绑定到指定部门。")
def create_person(payload: PersonCreate, db: Session = Depends(get_db)):
    _ensure_department(db, payload.department_id)
    now = now_iso()
    person = Person(
        id=make_id("person"),
        name=payload.name.strip(),
        department_id=payload.department_id,
        role=payload.role or "",
        email=payload.email or "",
        phone=payload.phone or "",
        created_at=now,
        updated_at=now,
    )
    db.add(person)
    db.commit()
    db.refresh(person)
    return person


@router.get("/{person_id}", response_model=PersonOut, summary="人员详情", description="根据人员 ID 查询人员详情。")
def get_person(person_id: str, db: Session = Depends(get_db)):
    person = db.get(Person, person_id)
    if not person:
        raise HTTPException(status_code=404, detail="人员不存在")
    return person


@router.put("/{person_id}", response_model=PersonOut, summary="更新人员", description="更新人员姓名、所属部门、角色、邮箱或电话。")
def update_person(
    person_id: str, payload: PersonUpdate, db: Session = Depends(get_db)
):
    person = db.get(Person, person_id)
    if not person:
        raise HTTPException(status_code=404, detail="人员不存在")
    data = payload.model_dump(exclude_unset=True)
    if "department_id" in data:
        _ensure_department(db, data["department_id"])
        person.department_id = data["department_id"]
    if "name" in data and data["name"] is not None:
        person.name = data["name"].strip()
    for field in ("role", "email", "phone"):
        if field in data and data[field] is not None:
            setattr(person, field, data[field])
    person.updated_at = now_iso()
    db.commit()
    db.refresh(person)
    return person


@router.delete("/{person_id}", summary="删除人员", description="删除指定人员资料。")
def delete_person(person_id: str, db: Session = Depends(get_db)):
    person = db.get(Person, person_id)
    if not person:
        raise HTTPException(status_code=404, detail="人员不存在")
    db.delete(person)
    db.commit()
    return {"detail": "已删除"}
