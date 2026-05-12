"""Session factory aligned with SQLAlchemy 2.x patterns."""

from __future__ import annotations

from contextlib import contextmanager
from typing import Generator

from sqlalchemy.orm import Session, sessionmaker

from database.connection import create_engine_from_settings, get_engine

SessionLocal: sessionmaker[Session] | None = None


def configure_session_factory() -> sessionmaker[Session]:
    """Bind sessionmaker to the configured engine."""
    global SessionLocal
    from config.settings import get_settings

    engine = create_engine_from_settings(get_settings())
    SessionLocal = sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
        future=True,
    )
    return SessionLocal


def get_session() -> Session:
    """Create a new database session (caller must close)."""
    if SessionLocal is None:
        configure_session_factory()
    assert SessionLocal is not None
    return SessionLocal()


@contextmanager
def session_scope() -> Generator[Session, None, None]:
    """
    Provide a transactional scope around a series of operations.

    Rolls back on exceptions and always closes the session.
    """
    if SessionLocal is None:
        configure_session_factory()
    assert SessionLocal is not None
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
