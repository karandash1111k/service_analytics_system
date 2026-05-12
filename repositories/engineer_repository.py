"""Persistence operations for engineers."""

from __future__ import annotations

from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from models.engineer import Engineer


class EngineerRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_id(self, engineer_id: int) -> Optional[Engineer]:
        return self._session.get(Engineer, engineer_id)

    def list_active(self) -> List[Engineer]:
        stmt = (
            select(Engineer)
            .where(Engineer.status == "active")
            .order_by(Engineer.full_name)
        )
        return list(self._session.scalars(stmt))

    def list_all(self, limit: int = 1000) -> List[Engineer]:
        stmt = select(Engineer).order_by(Engineer.id).limit(limit)
        return list(self._session.scalars(stmt))

    def list_with_orders_loaded(self, limit: int = 500) -> List[Engineer]:
        stmt = (
            select(Engineer)
            .options(selectinload(Engineer.service_orders))
            .order_by(Engineer.id)
            .limit(limit)
        )
        return list(self._session.scalars(stmt))

    def add(self, engineer: Engineer) -> Engineer:
        self._session.add(engineer)
        self._session.flush()
        return engineer
