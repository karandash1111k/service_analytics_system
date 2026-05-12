"""
Load stage — persists transformed entities via repositories.

Transactions are controlled by the caller (`pipeline` / integration runner).
"""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from typing import List

from sqlalchemy.orm import Session

from etl.transformer import NormalisedOrderRow, NormalisedRepairRow
from models.client import Client
from models.repair import Repair
from models.service_order import ServiceOrder
from repositories.client_repository import ClientRepository
from repositories.engineer_repository import EngineerRepository
from repositories.order_repository import OrderRepository
from repositories.repair_repository import RepairRepository
from utils.logger import get_logger

logger = get_logger(__name__)


class ETLLoader:
    def __init__(self, session: Session) -> None:
        self._session = session
        self._clients = ClientRepository(session)
        self._orders = OrderRepository(session)
        self._repairs = RepairRepository(session)
        self._engineers = EngineerRepository(session)

    def load_orders(self, rows: List[NormalisedOrderRow]) -> int:
        engineers = self._engineers.list_active()
        eng_ids = [e.id for e in engineers]
        inserted = 0
        for idx, row in enumerate(rows):
            client = Client(
                full_name=row.client_name,
                phone=row.client_phone,
                email=row.client_email,
                address="Импорт ETL",
            )
            self._clients.add(client)
            engineer_id = eng_ids[idx % len(eng_ids)] if eng_ids else None
            order = ServiceOrder(
                client_id=client.id,
                engineer_id=engineer_id,
                title=f"{row.title} [ext:{row.external_id}]",
                description=row.description,
                status=row.status,
                priority=row.priority,
                assigned_at=datetime.now(timezone.utc) if engineer_id else None,
            )
            self._orders.add(order)
            inserted += 1
        logger.info("ETL load_orders: inserted %s service orders", inserted)
        return inserted

    def load_repairs(self, rows: List[NormalisedRepairRow]) -> int:
        inserted = 0
        for row in rows:
            try:
                oid = int(row.external_order_ref)
            except ValueError:
                logger.warning("Repair skipped — invalid order ref %s", row.external_order_ref)
                continue
            order = self._orders.get_by_id(oid)
            if order is None:
                logger.warning("Repair skipped — order %s not found", oid)
                continue
            repair = Repair(
                order_id=oid,
                device_type=row.device_type,
                device_model=row.device_model,
                problem_description=row.problem_description,
                repair_status=row.repair_status,
                started_at=row.started_at,
                finished_at=row.finished_at,
                repair_cost=Decimal(str(round(row.repair_cost, 2))),
            )
            self._repairs.add(repair)
            inserted += 1
        logger.info("ETL load_repairs: inserted %s repairs", inserted)
        return inserted
