"""
Computes KPI snapshots and persists them for auditing / dashboards.

Delegates numerical logic to `analytics` package — services orchestrate only.
"""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from typing import List

from sqlalchemy.orm import Session

from analytics.engineer_kpi import EngineerKPIAggregator, EngineerOrderFact, EngineerRepairFact
from analytics.repair_statistics import RepairFact, RepairStatistics
from analytics.sla_calculator import OrderSLAInput, SLACalculator
from models.kpi_metric import KPIMetric
from repositories.engineer_repository import EngineerRepository
from repositories.order_repository import OrderRepository
from repositories.repair_repository import RepairRepository
from repositories.kpi_repository import KPIRepository
from utils.logger import get_logger

logger = get_logger(__name__)


class KPIService:
    def __init__(self, session: Session) -> None:
        self._session = session
        self._orders = OrderRepository(session)
        self._repairs = RepairRepository(session)
        self._engineers = EngineerRepository(session)
        self._kpi = KPIRepository(session)
        self._sla = SLACalculator()
        self._repair_stats = RepairStatistics()
        self._eng_agg = EngineerKPIAggregator()

    def compute_global_repair_stats(self) -> dict[str, float]:
        repairs = self._repairs.list_all_for_analytics()
        facts: List[RepairFact] = []
        for r in repairs:
            hours = None
            if r.started_at and r.finished_at:
                hours = (r.finished_at - r.started_at).total_seconds() / 3600.0
            facts.append(
                RepairFact(
                    repair_status=r.repair_status,
                    repair_cost=r.repair_cost,
                    duration_hours=hours,
                )
            )
        return self._repair_stats.summarise(facts)

    def compute_sla_summary(self) -> dict[str, float]:
        orders = self._orders.list_recent(limit=20_000)
        projections = [
            OrderSLAInput(
                order_id=o.id,
                priority=o.priority,
                status=o.status,
                created_at=o.created_at,
                completed_at=o.completed_at,
            )
            for o in orders
        ]
        return self._sla.summarise(projections)

    def snapshot_engineer_kpis(self) -> List[KPIMetric]:
        """Persist per-engineer KPI metrics row-by-row."""
        engineers = self._engineers.list_with_orders_loaded(limit=500)
        order_facts: List[EngineerOrderFact] = []
        repair_facts: List[EngineerRepairFact] = []

        repairs = self._repairs.list_all_for_analytics()

        for o in self._orders.list_recent(limit=20_000):
            eng_id = o.engineer_id or 0
            name = o.engineer.full_name if o.engineer else ""
            order_facts.append(
                EngineerOrderFact(
                    engineer_id=eng_id,
                    engineer_name=name,
                    order_status=o.status,
                )
            )

        for r in repairs:
            order = r.service_order
            eng_id = order.engineer_id or 0
            name = order.engineer.full_name if order.engineer else ""
            hours = None
            if r.started_at and r.finished_at:
                hours = (r.finished_at - r.started_at).total_seconds() / 3600.0
            repair_facts.append(
                EngineerRepairFact(
                    engineer_id=eng_id,
                    engineer_name=name,
                    repair_status=r.repair_status,
                    duration_hours=hours,
                )
            )

        orders_map = self._eng_agg.orders_per_engineer(order_facts)
        repairs_map = self._eng_agg.success_rates(repair_facts)
        workload = self._eng_agg.workload_index(orders_map, repairs_map)

        now = datetime.now(timezone.utc)
        metrics: List[KPIMetric] = []

        for eng in engineers:
            oid = eng.id
            orders_n = float(orders_map.get(oid, {}).get("orders", 0))
            sr = repairs_map.get(
                oid,
                {"successful": 0, "failed": 0, "total": 0, "success_pct": 0.0},
            )
            success_pct = float(sr.get("success_pct", 0.0))
            avg_dur = float(sr.get("avg_duration_hours", 0.0))
            wl_score = next(
                (w["workload_score"] for w in workload if w["engineer_id"] == oid),
                0.0,
            )
            pairs = [
                ("orders_assigned", orders_n),
                ("repair_success_pct", success_pct),
                ("avg_repair_duration_hours", avg_dur),
                ("workload_score", float(wl_score)),
            ]
            for name, val in pairs:
                metrics.append(
                    KPIMetric(
                        engineer_id=oid,
                        metric_name=name,
                        metric_value=Decimal(str(round(val, 6))),
                        calculated_at=now,
                    )
                )

        self._kpi.add_many(metrics)
        logger.info("KPI snapshot stored: %s metric rows", len(metrics))
        return metrics
