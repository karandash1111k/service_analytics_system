"""Persistence operations for KPI metric snapshots."""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from models.kpi_metric import KPIMetric


class KPIRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add_metric(self, metric: KPIMetric) -> KPIMetric:
        self._session.add(metric)
        self._session.flush()
        return metric

    def add_many(self, metrics: List[KPIMetric]) -> None:
        self._session.add_all(metrics)
        self._session.flush()

    def latest_for_engineer(
        self, engineer_id: int, metric_name: str
    ) -> Optional[KPIMetric]:
        stmt = (
            select(KPIMetric)
            .where(
                KPIMetric.engineer_id == engineer_id,
                KPIMetric.metric_name == metric_name,
            )
            .order_by(KPIMetric.calculated_at.desc())
            .limit(1)
        )
        return self._session.scalars(stmt).first()

    def list_recent(self, limit: int = 500) -> List[KPIMetric]:
        stmt = select(KPIMetric).order_by(KPIMetric.calculated_at.desc()).limit(limit)
        return list(self._session.scalars(stmt))

    def list_since(self, since: datetime, limit: int = 5000) -> List[KPIMetric]:
        stmt = (
            select(KPIMetric)
            .where(KPIMetric.calculated_at >= since)
            .order_by(KPIMetric.calculated_at.desc())
            .limit(limit)
        )
        return list(self._session.scalars(stmt))
