"""
Operational demand forecast — lightweight time-series helper.

Uses a simple moving average suitable for demonstration dashboards.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Iterable, List, Sequence


@dataclass(frozen=True)
class DailyOrderVolume:
    day: date
    count: int


class DemandForecast:
    def moving_average_next_day(self, series: Sequence[DailyOrderVolume], window: int = 7) -> float:
        """Return predicted orders for the next day as MA(window)."""
        if not series:
            return 0.0
        counts = [s.count for s in series]
        w = min(window, len(counts))
        tail = counts[-w:]
        return round(sum(tail) / len(tail), 3)

    def trend_slope_orders_per_day(self, series: Iterable[DailyOrderVolume]) -> float:
        """Least-squares slope for coarse trend visualisation."""
        pts: List[DailyOrderVolume] = list(series)
        n = len(pts)
        if n < 2:
            return 0.0
        xs = list(range(n))
        ys = [p.count for p in pts]
        mean_x = sum(xs) / n
        mean_y = sum(ys) / n
        num = sum((xs[i] - mean_x) * (ys[i] - mean_y) for i in range(n))
        den = sum((xs[i] - mean_x) ** 2 for i in range(n))
        if den == 0:
            return 0.0
        return round(num / den, 6)
