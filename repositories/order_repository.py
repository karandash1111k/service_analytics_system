"""Persistence operations for service orders."""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session, joinedload

from models.service_order import ServiceOrder


class OrderRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_id(self, order_id: int) -> Optional[ServiceOrder]:
        stmt = (
            select(ServiceOrder)
            .options(
                joinedload(ServiceOrder.client),
                joinedload(ServiceOrder.engineer),
                joinedload(ServiceOrder.repairs),
            )
            .where(ServiceOrder.id == order_id)
        )
        return self._session.scalars(stmt).unique().first()

    def list_recent(self, limit: int = 500) -> List[ServiceOrder]:
        stmt = (
            select(ServiceOrder)
            .options(joinedload(ServiceOrder.client), joinedload(ServiceOrder.engineer))
            .order_by(ServiceOrder.created_at.desc())
            .limit(limit)
        )
        return list(self._session.scalars(stmt).unique())

    def filter_orders(
        self,
        *,
        status: Optional[str] = None,
        engineer_id: Optional[int] = None,
        search: Optional[str] = None,
        limit: int = 500,
    ) -> List[ServiceOrder]:
        stmt: Select[tuple[ServiceOrder]] = select(ServiceOrder).options(
            joinedload(ServiceOrder.client),
            joinedload(ServiceOrder.engineer),
        )
        if status:
            stmt = stmt.where(ServiceOrder.status == status)
        if engineer_id is not None:
            stmt = stmt.where(ServiceOrder.engineer_id == engineer_id)
        if search:
            q = f"%{search.strip()}%"
            stmt = stmt.where(
                ServiceOrder.title.ilike(q) | ServiceOrder.description.ilike(q)
            )
        stmt = stmt.order_by(ServiceOrder.created_at.desc()).limit(limit)
        return list(self._session.scalars(stmt).unique())

    def count_by_engineer(self, engineer_id: int) -> int:
        stmt = select(func.count()).select_from(ServiceOrder).where(
            ServiceOrder.engineer_id == engineer_id
        )
        return int(self._session.scalar(stmt) or 0)

    def orders_created_between(
        self, start: datetime, end: datetime
    ) -> List[ServiceOrder]:
        stmt = (
            select(ServiceOrder)
            .where(ServiceOrder.created_at >= start, ServiceOrder.created_at <= end)
            .order_by(ServiceOrder.created_at)
        )
        return list(self._session.scalars(stmt))

    def add(self, order: ServiceOrder) -> ServiceOrder:
        self._session.add(order)
        self._session.flush()
        return order
