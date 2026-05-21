"""Aggregate all ORM models so that Base.metadata sees them."""
from .department import Department  # noqa: F401
from .meeting import Meeting  # noqa: F401
from .person import Person  # noqa: F401
from .settings import Settings  # noqa: F401
from .task import Task  # noqa: F401
