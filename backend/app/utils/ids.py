"""ID and timestamp helpers."""
import secrets
from datetime import datetime, timezone


def make_id(prefix: str) -> str:
    """Generate an ID like `prefix_xxxxxxxx` with 8 hex chars."""
    return f"{prefix}_{secrets.token_hex(4)}"


def now_iso() -> str:
    """Current UTC time as ISO 8601 string with seconds precision."""
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def mask_key(key: str | None) -> str:
    """Mask an API key, keeping the first 4 characters."""
    if not key:
        return ""
    if len(key) <= 4:
        return "****"
    return key[:4] + "****"
