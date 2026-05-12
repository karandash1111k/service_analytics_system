"""Facade assembling analytical artefacts for UI / exports."""

from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
from typing import Any, Dict, List

import pandas as pd
from sqlalchemy.orm import Session

from analytics.forecast_module import DailyOrderVolume, DemandForecast
from analytics.repair_statistics import RepairFact, RepairStatistics
from analytics.sla_calculator import OrderSLAInput, SLACalculator
from repositories.order_repository import OrderRepository
from repositories.repair_repository import RepairRepository
from repositories.kpi_repository import KPIRepository

from services.kpi_service import KPIService


class AnalyticsService:
    def __init__(self, session: Session) -> None:
        self._session = session
        self._orders = OrderRepository(session)
        self._repairs = RepairRepository(session)
        self._kpi_repo = KPIRepository(session)
        self._kpi = KPIService(session)
        self._sla = SLACalculator()
        self._repair_stats = RepairStatistics()
        self._forecast = DemandForecast()

    def sla_dashboard(self) -> Dict[str, float]:
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

    def repair_dashboard(self) -> Dict[str, float]:
        return self._kpi.compute_global_repair_stats()

    def orders_per_day_frame(self) -> pd.DataFrame:
        orders = self._orders.list_recent(limit=20_000)
        if not orders:
            return pd.DataFrame(columns=["day", "count"])
        rows = []
        for o in orders:
            created = o.created_at
            if created.tzinfo is None:
                created = created.replace(tzinfo=timezone.utc)
            d = created.date()
            rows.append({"day": d, "order_id": o.id})
        df = pd.DataFrame(rows)
        g = df.groupby("day").agg(count=("order_id", "count")).reset_index()
        g.sort_values("day", inplace=True)
        return g

    def forecast_next_day_orders(self) -> float:
        g = self.orders_per_day_frame()
        series = [DailyOrderVolume(day=r.day, count=int(r.count)) for r in g.itertuples()]
        return self._forecast.moving_average_next_day(series, window=7)

    def engineer_workload_frame(self) -> pd.DataFrame:
        orders = self._orders.list_recent(limit=20_000)
        if not orders:
            return pd.DataFrame(columns=["engineer", "orders"])
        rows = []
        for o in orders:
            if o.engineer_id is None:
                continue
            rows.append(
                {
                    "engineer": o.engineer.full_name if o.engineer else str(o.engineer_id),
                    "order_id": o.id,
                }
            )
        if not rows:
            return pd.DataFrame(columns=["engineer", "orders"])
        df = pd.DataFrame(rows)
        return (
            df.groupby("engineer")
            .agg(orders=("order_id", "count"))
            .reset_index()
            .sort_values("orders", ascending=False)
        )

    def repairs_outcome_frame(self) -> pd.DataFrame:
        repairs = self._repairs.list_all_for_analytics()
        facts = []
        for r in repairs:
            facts.append(r.repair_status)
        c = Counter(facts)
        return pd.DataFrame(
            {"status": list(c.keys()), "count": list(c.values())}
        ).sort_values("count", ascending=False)

    def repair_duration_distribution(self) -> pd.DataFrame:
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
        df = pd.DataFrame(
            [
                {
                    "duration_hours": f.duration_hours,
                    "status": f.repair_status,
                }
                for f in facts
                if f.duration_hours is not None
            ]
        )
        return df

    def latest_kpi_table(self) -> pd.DataFrame:
        metrics = self._kpi_repo.list_recent(limit=2000)
        if not metrics:
            return pd.DataFrame(columns=["engineer_id", "metric_name", "metric_value", "calculated_at"])
        rows = []
        for m in metrics:
            rows.append(
                {
                    "engineer_id": m.engineer_id,
                    "metric_name": m.metric_name,
                    "metric_value": float(m.metric_value),
                    "calculated_at": m.calculated_at,
                }
            )
        return pd.DataFrame(rows)

    def executive_summary(self) -> Dict[str, Any]:
        """Single payload for dashboards / PDF cover page."""
        sla = self.sla_dashboard()
        rep = self.repair_dashboard()
        return {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "sla": sla,
            "repairs": rep,
            "forecast_next_day_orders": self.forecast_next_day_orders(),
        }

    def sla_breach_rate_by_priority_frame(self) -> pd.DataFrame:
        """Share of SLA breaches grouped by ticket priority (for charts)."""
        orders = self._orders.list_recent(limit=5000)
        if not orders:
            return pd.DataFrame(columns=["priority", "breach_pct"])
        now = datetime.now(timezone.utc)
        buckets: Dict[str, List[float]] = {}
        for o in orders:
            res = self._sla.evaluate_order(
                OrderSLAInput(
                    order_id=o.id,
                    priority=o.priority,
                    status=o.status,
                    created_at=o.created_at,
                    completed_at=o.completed_at,
                ),
                now=now,
            )
            buckets.setdefault(o.priority, []).append(1.0 if res.breached else 0.0)
        priorities = sorted(buckets.keys())
        breach_pct = [
            round(100.0 * sum(buckets[p]) / len(buckets[p]), 2) if buckets[p] else 0.0
            for p in priorities
        ]
        return pd.DataFrame({"priority": priorities, "breach_pct": breach_pct})
