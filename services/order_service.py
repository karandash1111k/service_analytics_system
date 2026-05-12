"""Business workflows around service orders (assignment, status transitions)."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy.orm import Session

from models.service_order import ServiceOrder
from repositories.engineer_repository import EngineerRepository
from repositories.order_repository import OrderRepository
from utils.logger import get_logger

logger = get_logger(__name__)


class OrderService:
    def __init__(self, session: Session) -> None:
        self._session = session
        self._orders = OrderRepository(session)
        self._engineers = EngineerRepository(session)

    def list_orders(
        self,
        *,
        status: Optional[str] = None,
        engineer_id: Optional[int] = None,
        search: Optional[str] = None,
    ) -> List[ServiceOrder]:
        return self._orders.filter_orders(
            status=status, engineer_id=engineer_id, search=search
        )

    def assign_engineer(self, order_id: int, engineer_id: int) -> ServiceOrder:
        """Assign engineer if engineer exists and is active."""
        order = self._orders.get_by_id(order_id)
        if order is None:
            raise ValueError("Заявка не найдена")
        engineer = self._engineers.get_by_id(engineer_id)
        if engineer is None:
            raise ValueError("Инженер не найден")
        if engineer.status != "active":
            raise ValueError("Инженер недоступен (не active)")
        order.engineer_id = engineer_id
        order.status = "assigned"
        order.assigned_at = datetime.now(timezone.utc)
        self._session.add(order)
        self._session.flush()
        logger.info("Order %s assigned to engineer %s", order_id, engineer_id)
        return order

    def mark_completed(self, order_id: int) -> ServiceOrder:
        order = self._orders.get_by_id(order_id)
        if order is None:
            raise ValueError("Заявка не найдена")
        order.status = "completed"
        order.completed_at = datetime.now(timezone.utc)
        self._session.add(order)
        self._session.flush()
        logger.info("Order %s completed", order_id)
        return order
