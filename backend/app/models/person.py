"""Person ORM model."""
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from ..database import Base


class Person(Base):
    __tablename__ = "people"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    department_id: Mapped[str | None] = mapped_column(
        String(64), ForeignKey("departments.id", ondelete="SET NULL"), nullable=True
    )
    role: Mapped[str] = mapped_column(String(128), default="", nullable=False)
    email: Mapped[str] = mapped_column(String(255), default="", nullable=False)
    phone: Mapped[str] = mapped_column(String(64), default="", nullable=False)
    created_at: Mapped[str] = mapped_column(String(32), nullable=False)
    updated_at: Mapped[str] = mapped_column(String(32), nullable=False)
