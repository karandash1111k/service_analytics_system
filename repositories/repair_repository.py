"""Persistence operations for repairs."""

from __future__ import annotations

from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from models.repair import Repair


class RepairRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_id(self, repair_id: int) -> Optional[Repair]:
        stmt = (
            select(Repair)
            .options(
                joinedload(Repair.service_order),
                joinedload(Repair.spare_parts),
            )
            .where(Repair.id == repair_id)
        )
        return self._session.scalars(stmt).unique().first()

    def list_recent(self, limit: int = 500) -> List[Repair]:
        stmt = (
            select(Repair)
            .options(joinedload(Repair.service_order))
            .order_by(Repair.id.desc())
            .limit(limit)
        )
        return list(self._session.scalars(stmt).unique())

    def filter_repairs(
        self,
        *,
        status: Optional[str] = None,
        limit: int = 500,
    ) -> List[Repair]:
        stmt = select(Repair).options(joinedload(Repair.service_order))
        if status:
            stmt = stmt.where(Repair.repair_status == status)
        stmt = stmt.order_by(Repair.id.desc()).limit(limit)
        return list(self._session.scalars(stmt).unique())

    def list_all_for_analytics(self, limit: int = 50_000) -> List[Repair]:
        stmt = (
            select(Repair)
            .options(joinedload(Repair.service_order))
            .order_by(Repair.id)
            .limit(limit)
        )
        return list(self._session.scalars(stmt).unique())

    def add(self, repair: Repair) -> Repair:
        self._session.add(repair)
        self._session.flush()
        return repair
