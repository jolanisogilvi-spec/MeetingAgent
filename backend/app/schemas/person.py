"""Pydantic schemas for Person."""
from pydantic import BaseModel, ConfigDict, Field


class PersonCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=128, description="人员姓名")
    department_id: str | None = Field(default=None, description="所属部门 ID；可为空")
    role: str = Field(default="", description="职位或角色")
    email: str = Field(default="", description="邮箱")
    phone: str = Field(default="", description="电话")


class PersonUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=128, description="人员姓名")
    department_id: str | None = Field(default=None, description="所属部门 ID；可为空")
    role: str | None = Field(default=None, description="职位或角色")
    email: str | None = Field(default=None, description="邮箱")
    phone: str | None = Field(default=None, description="电话")


class PersonOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(description="人员 ID")
    name: str = Field(description="人员姓名")
    department_id: str | None = Field(description="所属部门 ID；可为空")
    role: str = Field(description="职位或角色")
    email: str = Field(description="邮箱")
    phone: str = Field(description="电话")
    created_at: str = Field(description="创建时间，ISO 8601 字符串")
    updated_at: str = Field(description="更新时间，ISO 8601 字符串")
