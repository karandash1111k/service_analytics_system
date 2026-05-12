"""Repair-level descriptive statistics."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Iterable, List


@dataclass(frozen=True)
class RepairFact:
    repair_status: str
    repair_cost: Decimal
    duration_hours: float | None


class RepairStatistics:
    def summarise(self, repairs: Iterable[RepairFact]) -> dict[str, float]:
        items: List[RepairFact] = list(repairs)
        if not items:
            return {
                "count": 0.0,
                "success_pct": 0.0,
                "failure_pct": 0.0,
                "avg_cost": 0.0,
                "avg_duration_hours": 0.0,
            }
        success = sum(1 for r in items if r.repair_status.lower() == "successful")
        failed = sum(1 for r in items if r.repair_status.lower() == "failed")
        n = len(items)
        costs = [float(r.repair_cost) for r in items]
        durations = [r.duration_hours for r in items if r.duration_hours is not None]
        return {
            "count": float(n),
            "success_pct": round(100.0 * success / n, 2),
            "failure_pct": round(100.0 * failed / n, 2),
            "avg_cost": round(sum(costs) / n, 2),
            "avg_duration_hours": (
                round(sum(durations) / len(durations), 3) if durations else 0.0
            ),
        }
