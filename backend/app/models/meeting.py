"""Meeting ORM model."""
from sqlalchemy import JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from ..database import Base


class Meeting(Base):
    __tablename__ = "meetings"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    meeting_time: Mapped[str] = mapped_column(String(32), default="", nullable=False)
    department_id: Mapped[str] = mapped_column(String(64), default="", nullable=False)
    participant_ids: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    meeting_type: Mapped[str] = mapped_column(String(64), default="", nullable=False)
    objective: Mapped[str] = mapped_column(Text, default="", nullable=False)
    notes: Mapped[str] = mapped_column(Text, default="", nullable=False)

    status: Mapped[str] = mapped_column(String(32), default="draft", nullable=False)
    raw_text: Mapped[str] = mapped_column(Text, default="", nullable=False)
    summary: Mapped[str] = mapped_column(Text, default="", nullable=False)
    meeting_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    error_message: Mapped[str] = mapped_column(Text, default="", nullable=False)

    audio_filename: Mapped[str] = mapped_column(String(255), default="", nullable=False)
    kb_filenames: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    prep_data: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)

    created_at: Mapped[str] = mapped_column(String(32), nullable=False)
    updated_at: Mapped[str] = mapped_column(String(32), nullable=False)
