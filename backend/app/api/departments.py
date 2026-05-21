"""Department REST endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.department import Department
from ..models.person import Person
from ..schemas.department import DepartmentCreate, DepartmentOut, DepartmentUpdate
from ..utils.ids import make_id, now_iso

router = APIRouter(prefix="/departments", tags=["部门管理"])


@router.get("", response_model=list[DepartmentOut], summary="部门列表", description="查询全部部门，按创建时间倒序返回。")
def list_departments(db: Session = Depends(get_db)):
    return db.query(Department).order_by(Department.created_at.desc()).all()


@router.post("", response_model=DepartmentOut, summary="创建部门", description="创建一个新的部门。")
def create_department(payload: DepartmentCreate, db: Session = Depends(get_db)):
    now = now_iso()
    dept = Department(
        id=make_id("dept"),
        name=payload.name.strip(),
        description=payload.description or "",
        created_at=now,
        updated_at=now,
    )
    db.add(dept)
    db.commit()
    db.refresh(dept)
    return dept


@router.get("/{department_id}", response_model=DepartmentOut, summary="部门详情", description="根据部门 ID 查询部门详情。")
def get_department(department_id: str, db: Session = Depends(get_db)):
    dept = db.get(Department, department_id)
    if not dept:
        raise HTTPException(status_code=404, detail="部门不存在")
    return dept


@router.put("/{department_id}", response_model=DepartmentOut, summary="更新部门", description="更新部门名称或描述。")
def update_department(
    department_id: str, payload: DepartmentUpdate, db: Session = Depends(get_db)
):
    dept = db.get(Department, department_id)
    if not dept:
        raise HTTPException(status_code=404, detail="部门不存在")
    data = payload.model_dump(exclude_unset=True)
    if "name" in data and data["name"] is not None:
        dept.name = data["name"].strip()
    if "description" in data and data["description"] is not None:
        dept.description = data["description"]
    dept.updated_at = now_iso()
    db.commit()
    db.refresh(dept)
    return dept


@router.delete("/{department_id}", summary="删除部门", description="删除部门；关联人员会自动变为未分配部门。")
def delete_department(department_id: str, db: Session = Depends(get_db)):
    dept = db.get(Department, department_id)
    if not dept:
        raise HTTPException(status_code=404, detail="部门不存在")
    now = now_iso()
    for person in db.query(Person).filter(Person.department_id == department_id).all():
        person.department_id = None
        person.updated_at = now
    db.delete(dept)
    db.commit()
    return {"detail": "已删除"}
