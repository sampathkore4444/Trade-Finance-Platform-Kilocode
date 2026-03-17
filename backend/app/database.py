"""
Database Configuration - Re-export from core for backward compatibility
"""

from app.core.database import (
    get_db,
    init_db,
    drop_db,
    Base,
    engine,
    AsyncSessionLocal,
)

__all__ = [
    "get_db",
    "init_db",
    "drop_db",
    "Base",
    "engine",
    "AsyncSessionLocal",
]
