"""Task ORM model."""
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from ..database import Base


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    meeting_id: Mapped[str | None] = mapped_column(
        String(64), ForeignKey("meetings.id", ondelete="SET NULL"), nullable=True
    )
    department_id: Mapped[str] = mapped_column(String(64), default="", nullable=False)
    owner_name: Mapped[str] = mapped_column(String(128), default="", nullable=False)
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    due_date: Mapped[str] = mapped_column(String(32), default="", nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="todo", nullable=False)
    created_at: Mapped[str] = mapped_column(String(32), nullable=False)
    updated_at: Mapped[str] = mapped_column(String(32), nullable=False)
