"""Pydantic schemas for Meeting."""
from pydantic import BaseModel, ConfigDict, Field


class MeetingCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255, description="会议名称")
    meeting_time: str = Field(default="", description="会议时间，建议使用 ISO 8601 字符串")
    department_id: str = Field(default="", description="所属部门 ID")
    participant_ids: list[str] = Field(default_factory=list, description="参会人员 ID 列表")
    meeting_type: str = Field(default="", description="会议类型，例如周会、评审会、决策会")
    objective: str = Field(default="", description="会议目标")
    notes: str = Field(default="", description="备注")
    raw_text: str = Field(default="", description="会议原文，可创建时直接保存")


class MeetingUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255, description="会议名称")
    meeting_time: str | None = Field(default=None, description="会议时间")
    department_id: str | None = Field(default=None, description="所属部门 ID")
    participant_ids: list[str] | None = Field(default=None, description="参会人员 ID 列表")
    meeting_type: str | None = Field(default=None, description="会议类型")
    objective: str | None = Field(default=None, description="会议目标")
    notes: str | None = Field(default=None, description="备注")
    status: str | None = Field(default=None, description="会议状态：draft、generating、completed、confirmed、failed")
    raw_text: str | None = Field(default=None, description="会议原文")
    summary: str | None = Field(default=None, description="AI 生成的会议摘要")
    meeting_json: dict | None = Field(default=None, description="结构化会议纪要 JSON；保存后会同步待办任务")
    error_message: str | None = Field(default=None, description="生成失败时的错误信息")
    audio_filename: str | None = Field(default=None, description="上传的会议文件名")
    kb_filenames: list[str] | None = Field(default=None, description="上传的知识库参考文件名列表")


class MeetingOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(description="会议 ID")
    title: str = Field(description="会议名称")
    meeting_time: str = Field(description="会议时间")
    department_id: str = Field(description="所属部门 ID")
    participant_ids: list[str] = Field(description="参会人员 ID 列表")
    meeting_type: str = Field(description="会议类型")
    objective: str = Field(description="会议目标")
    notes: str = Field(description="备注")
    status: str = Field(description="会议状态：draft、generating、completed、confirmed、failed")
    raw_text: str = Field(description="会议原文")
    summary: str = Field(description="AI 生成的会议摘要")
    meeting_json: dict = Field(description="结构化会议纪要 JSON")
    error_message: str = Field(description="生成失败时的错误信息")
    audio_filename: str = Field(description="上传的会议文件名")
    kb_filenames: list[str] = Field(description="上传的知识库参考文件名列表")
    created_at: str = Field(description="创建时间，ISO 8601 字符串")
    updated_at: str = Field(description="更新时间，ISO 8601 字符串")
