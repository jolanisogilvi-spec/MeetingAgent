"""SQLAlchemy engine, session, and base."""
from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session

from .config import DB_URL, ensure_dirs

engine = create_engine(
    DB_URL,
    echo=False,
    future=True,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


class Base(DeclarativeBase):
    pass


def get_db():
    """FastAPI dependency that yields a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Create runtime dirs and all tables on startup."""
    ensure_dirs()
    from . import models  # noqa: F401  ensure models are imported

    Base.metadata.create_all(bind=engine)
    _ensure_meeting_prep_data_column()


def _ensure_meeting_prep_data_column() -> None:
    """Add lightweight SQLite-compatible columns that older databases lack."""
    default_value = '{"common_files":[],"participants":{}}'
    with engine.begin() as conn:
        rows = conn.execute(text("PRAGMA table_info(meetings)")).mappings().all()
        columns = {row["name"] for row in rows}
        if "prep_data" not in columns:
            conn.execute(
                text(
                    "ALTER TABLE meetings "
                    f"ADD COLUMN prep_data JSON NOT NULL DEFAULT '{default_value}'"
                )
            )
