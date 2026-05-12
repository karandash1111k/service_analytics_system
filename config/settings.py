"""
Centralised configuration loaded from environment variables.

Uses python-dotenv for local `.env` files without committing secrets.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from urllib.parse import quote_plus

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    """Immutable runtime settings."""

    db_host: str
    db_port: int
    db_name: str
    db_user: str
    db_password: str
    app_log_level: str

    @property
    def sqlalchemy_database_uri(self) -> str:
        """SQLAlchemy URI for MySQL via PyMySQL driver."""
        user = quote_plus(self.db_user)
        password = quote_plus(self.db_password)
        host = self.db_host
        port = self.db_port
        name = self.db_name
        return (
            f"mysql+pymysql://{user}:{password}@{host}:{port}/{name}"
            "?charset=utf8mb4"
        )


def _read_env() -> Settings:
    host = os.getenv("DB_HOST", "localhost")
    port = int(os.getenv("DB_PORT", "3306"))
    name = os.getenv("DB_NAME", "service_analytics")
    user = os.getenv("DB_USER", "root")
    password = os.getenv("DB_PASSWORD", "")
    level = os.getenv("APP_LOG_LEVEL", "INFO").upper()
    return Settings(
        db_host=host,
        db_port=port,
        db_name=name,
        db_user=user,
        db_password=password,
        app_log_level=level,
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached settings singleton."""
    return _read_env()
