"""
SQLAlchemy engine lifecycle.

Separated from session handling to keep concerns isolated (enterprise layering).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

if TYPE_CHECKING:
    from config.settings import Settings

_engine: Engine | None = None


def create_engine_from_settings(settings: "Settings") -> Engine:
    """Create (or return cached) SQLAlchemy engine for MySQL."""
    global _engine
    if _engine is None:
        _engine = create_engine(
            settings.sqlalchemy_database_uri,
            pool_pre_ping=True,
            pool_recycle=3600,
            echo=False,
            future=True,
        )
    return _engine


def get_engine() -> Engine:
    """Return active engine; raises if not initialised."""
    if _engine is None:
        raise RuntimeError("Engine not initialised. Call create_engine_from_settings first.")
    return _engine


def dispose_engine() -> None:
    """Dispose pooled connections on shutdown."""
    global _engine
    if _engine is not None:
        _engine.dispose()
        _engine = None
