"""Pydantic schemas for Task."""
from pydantic import BaseModel, ConfigDict, Field


class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=512, description="任务标题或待办内容")
    meeting_id: str | None = Field(default=None, description="来源会议 ID；手动任务可为空")
    department_id: str = Field(default="", description="所属部门 ID")
    owner_name: str = Field(default="", description="责任人姓名")
    due_date: str = Field(default="", description="截止时间，可为自然语言或日期字符串")
    status: str = Field(default="todo", description="任务状态：todo、doing、done、delayed")


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=512, description="任务标题或待办内容")
    meeting_id: str | None = Field(default=None, description="来源会议 ID")
    department_id: str | None = Field(default=None, description="所属部门 ID")
    owner_name: str | None = Field(default=None, description="责任人姓名")
    due_date: str | None = Field(default=None, description="截止时间，可为自然语言或日期字符串")
    status: str | None = Field(default=None, description="任务状态：todo、doing、done、delayed")


class TaskOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(description="任务 ID")
    meeting_id: str | None = Field(description="来源会议 ID")
    department_id: str = Field(description="所属部门 ID")
    owner_name: str = Field(description="责任人姓名")
    title: str = Field(description="任务标题或待办内容")
    due_date: str = Field(description="截止时间")
    status: str = Field(description="任务状态：todo、doing、done、delayed")
    created_at: str = Field(description="创建时间，ISO 8601 字符串")
    updated_at: str = Field(description="更新时间，ISO 8601 字符串")
