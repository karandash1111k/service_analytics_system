"""Schema bootstrap — creates tables from declarative metadata."""

from __future__ import annotations

from sqlalchemy.engine import Engine

from models import Base


def create_all_tables(engine: Engine) -> None:
    """Create every registered table (development / demo environments)."""
    Base.metadata.create_all(bind=engine)
