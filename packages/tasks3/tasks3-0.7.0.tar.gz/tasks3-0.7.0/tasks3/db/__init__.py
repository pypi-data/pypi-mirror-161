"""Database for tasks3"""

from tasks3.db.db import init, drop, purge  # noqa: F401
from tasks3.db.models import Task  # noqa: F401

from tasks3.db.extension import session_scope  # noqa: F401

__all__ = [
    "init",
    "drop",
    "purge",
    "session_scope",
    "Task",
]
