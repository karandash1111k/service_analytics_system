"""Persistence operations for integration audit logs."""

from __future__ import annotations

from typing import List

from sqlalchemy import select
from sqlalchemy.orm import Session

from models.integration_log import IntegrationLog


class IntegrationLogRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, log: IntegrationLog) -> IntegrationLog:
        self._session.add(log)
        self._session.flush()
        return log

    def list_recent(self, limit: int = 200) -> List[IntegrationLog]:
        stmt = (
            select(IntegrationLog)
            .order_by(IntegrationLog.created_at.desc())
            .limit(limit)
        )
        return list(self._session.scalars(stmt))
