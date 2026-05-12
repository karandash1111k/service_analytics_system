"""Persistence operations for synchronisation batch history."""

from __future__ import annotations

from typing import List

from sqlalchemy import select
from sqlalchemy.orm import Session

from models.sync_history import SyncHistory


class SyncHistoryRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, row: SyncHistory) -> SyncHistory:
        self._session.add(row)
        self._session.flush()
        return row

    def update(self, row: SyncHistory) -> SyncHistory:
        self._session.add(row)
        self._session.flush()
        return row

    def list_recent(self, limit: int = 100) -> List[SyncHistory]:
        stmt = (
            select(SyncHistory)
            .order_by(SyncHistory.started_at.desc())
            .limit(limit)
        )
        return list(self._session.scalars(stmt))
