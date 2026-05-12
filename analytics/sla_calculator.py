"""
SLA analytics for service orders.

Computes breach detection using configurable targets per priority.
Pure functions receive pre-loaded dataclass rows from the service layer.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Iterable, List, Optional

from utils.constants import DEFAULT_SLA_HOURS, SLA_HOURS_BY_PRIORITY


def _aware(dt: Optional[datetime]) -> Optional[datetime]:
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


@dataclass(frozen=True)
class OrderSLAInput:
    """Minimal order projection for SLA evaluation."""

    order_id: int
    priority: str
    status: str
    created_at: datetime
    completed_at: Optional[datetime]


@dataclass(frozen=True)
class SLAOrderResult:
    order_id: int
    priority: str
    target_hours: float
    elapsed_hours: Optional[float]
    breached: bool
    resolved: bool


class SLACalculator:
    """Enterprise SLA engine — deterministic and testable."""

    def __init__(self, sla_map: Optional[dict[str, float]] = None) -> None:
        self._sla_map = sla_map if sla_map is not None else SLA_HOURS_BY_PRIORITY

    def target_hours(self, priority: str) -> float:
        key = (priority or "").strip().lower()
        return float(self._sla_map.get(key, DEFAULT_SLA_HOURS))

    def evaluate_order(self, row: OrderSLAInput, now: Optional[datetime] = None) -> SLAOrderResult:
        """Return SLA evaluation for a single order."""
        created = _aware(row.created_at)
        completed = _aware(row.completed_at)
        target_h = self.target_hours(row.priority)
        resolved = row.status.lower() in {"completed", "cancelled"}
        reference_end = completed if completed is not None else _aware(now or datetime.now(timezone.utc))
        assert created is not None and reference_end is not None
        elapsed = (reference_end - created).total_seconds() / 3600.0
        breached = elapsed > target_h and row.status.lower() != "cancelled"
        return SLAOrderResult(
            order_id=row.order_id,
            priority=row.priority,
            target_hours=target_h,
            elapsed_hours=elapsed if resolved or completed else elapsed,
            breached=breached,
            resolved=resolved,
        )

    def summarise(self, rows: Iterable[OrderSLAInput]) -> dict[str, float]:
        """Aggregate SLA KPIs for dashboard consumption."""
        items = list(rows)
        if not items:
            return {
                "orders_evaluated": 0.0,
                "sla_met_pct": 0.0,
                "sla_breach_pct": 0.0,
                "avg_resolution_hours": 0.0,
            }
        now = datetime.now(timezone.utc)
        evaluations = [self.evaluate_order(r, now=now) for r in items]
        resolved = [e for e in evaluations if e.resolved]
        breached_count = sum(1 for e in evaluations if e.breached)
        met_count = sum(1 for e in evaluations if not e.breached)
        avg_hours = 0.0
        if resolved:
            hours = [e.elapsed_hours for e in resolved if e.elapsed_hours is not None]
            avg_hours = sum(hours) / len(hours) if hours else 0.0
        n = len(evaluations)
        return {
            "orders_evaluated": float(n),
            "sla_met_pct": round(100.0 * met_count / n, 2),
            "sla_breach_pct": round(100.0 * breached_count / n, 2),
            "avg_resolution_hours": round(avg_hours, 3),
        }
