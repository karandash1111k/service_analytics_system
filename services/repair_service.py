"""Repair lifecycle operations."""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from typing import List, Optional

from sqlalchemy.orm import Session

from models.repair import Repair
from repositories.order_repository import OrderRepository
from repositories.repair_repository import RepairRepository
from repositories.spare_part_repository import SparePartRepository
from utils.logger import get_logger

logger = get_logger(__name__)


class RepairService:
    def __init__(self, session: Session) -> None:
        self._session = session
        self._repairs = RepairRepository(session)
        self._orders = OrderRepository(session)
        self._parts = SparePartRepository(session)

    def list_repairs(self, *, status: Optional[str] = None) -> List[Repair]:
        return self._repairs.filter_repairs(status=status)

    def create_repair(
        self,
        order_id: int,
        *,
        device_type: str,
        device_model: str,
        problem_description: str,
        repair_status: str = "pending",
        repair_cost: Decimal = Decimal("0"),
    ) -> Repair:
        order = self._orders.get_by_id(order_id)
        if order is None:
            raise ValueError("Заявка не найдена")
        repair = Repair(
            order_id=order_id,
            device_type=device_type.strip(),
            device_model=device_model.strip(),
            problem_description=problem_description.strip(),
            repair_status=repair_status,
            repair_cost=repair_cost,
            started_at=datetime.now(timezone.utc),
        )
        self._repairs.add(repair)
        if order.status in {"assigned", "new"}:
            order.status = "in_progress"
            self._session.add(order)
        self._session.flush()
        logger.info("Repair created for order %s", order_id)
        return repair

    def attach_spare_parts(self, repair_id: int, part_numbers: List[str]) -> Repair:
        repair = self._repairs.get_by_id(repair_id)
        if repair is None:
            raise ValueError("Ремонт не найден")
        for pn in part_numbers:
            part = self._parts.get_by_part_number(pn.strip())
            if part is None:
                raise ValueError(f"Запчасть не найдена: {pn}")
            if part not in repair.spare_parts:
                repair.spare_parts.append(part)
        self._session.add(repair)
        self._session.flush()
        return repair
