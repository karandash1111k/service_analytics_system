"""Persistence operations for spare parts inventory."""

from __future__ import annotations

from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from models.spare_part import SparePart


class SparePartRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_id(self, part_id: int) -> Optional[SparePart]:
        return self._session.get(SparePart, part_id)

    def get_by_part_number(self, part_number: str) -> Optional[SparePart]:
        stmt = select(SparePart).where(SparePart.part_number == part_number)
        return self._session.scalars(stmt).first()

    def list_all(self, limit: int = 2000) -> List[SparePart]:
        stmt = select(SparePart).order_by(SparePart.name).limit(limit)
        return list(self._session.scalars(stmt))

    def add(self, part: SparePart) -> SparePart:
        self._session.add(part)
        self._session.flush()
        return part
