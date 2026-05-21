"""Settings ORM model (single-row, id=1)."""
from sqlalchemy import Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from ..database import Base


class Settings(Base):
    __tablename__ = "settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    llm_api_key: Mapped[str] = mapped_column(Text, default="", nullable=False)
    llm_base_url: Mapped[str] = mapped_column(Text, default="", nullable=False)
    llm_model_name: Mapped[str] = mapped_column(String(255), default="", nullable=False)

    embedding_api_key: Mapped[str] = mapped_column(Text, default="", nullable=False)
    embedding_base_url: Mapped[str] = mapped_column(Text, default="", nullable=False)
    embedding_model_name: Mapped[str] = mapped_column(String(255), default="", nullable=False)

    speech_provider: Mapped[str] = mapped_column(String(32), default="local", nullable=False)
    speech_model_type: Mapped[str] = mapped_column(String(64), default="", nullable=False)
    speech_api_key: Mapped[str] = mapped_column(Text, default="", nullable=False)
    speech_base_url: Mapped[str] = mapped_column(Text, default="", nullable=False)
    speech_model_name: Mapped[str] = mapped_column(String(255), default="", nullable=False)

    temperature: Mapped[float] = mapped_column(Float, default=0.3, nullable=False)
    max_tokens: Mapped[int] = mapped_column(Integer, default=1024, nullable=False)

    updated_at: Mapped[str] = mapped_column(String(32), default="", nullable=False)
