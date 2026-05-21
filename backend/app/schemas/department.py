"""Pydantic schemas for Department."""
from pydantic import BaseModel, ConfigDict, Field


class DepartmentCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=128, description="部门名称")
    description: str = Field(default="", description="部门描述")


class DepartmentUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=128, description="部门名称")
    description: str | None = Field(default=None, description="部门描述")


class DepartmentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(description="部门 ID")
    name: str = Field(description="部门名称")
    description: str = Field(description="部门描述")
    created_at: str = Field(description="创建时间，ISO 8601 字符串")
    updated_at: str = Field(description="更新时间，ISO 8601 字符串")
