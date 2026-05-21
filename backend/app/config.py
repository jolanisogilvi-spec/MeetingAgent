"""Application configuration: paths and database URL."""
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
UPLOAD_DIR = DATA_DIR / "uploads"
EXPORT_DIR = DATA_DIR / "exports"
DB_PATH = DATA_DIR / "app.db"
DB_URL = f"sqlite:///{DB_PATH}"

CORS_ORIGINS = ["http://localhost:5173", "http://localhost:8050"]

MAX_UPLOAD_SIZE = 50 * 1024 * 1024
MEETING_UPLOAD_EXTS = {".mp3", ".wav", ".txt", ".docx"}
KB_UPLOAD_EXTS = {".txt", ".docx"}


def ensure_dirs() -> None:
    """Create all required runtime directories."""
    for d in (DATA_DIR, UPLOAD_DIR, EXPORT_DIR):
        d.mkdir(parents=True, exist_ok=True)
