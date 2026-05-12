"""
Engineer-centric KPI aggregation.

Produces workload, throughput, and coarse efficiency indicators.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List


@dataclass(frozen=True)
class EngineerOrderFact:
    engineer_id: int
    engineer_name: str
    order_status: str


@dataclass(frozen=True)
class EngineerRepairFact:
    engineer_id: int
    engineer_name: str
    repair_status: str
    duration_hours: float | None


class EngineerKPIAggregator:
    def orders_per_engineer(self, facts: Iterable[EngineerOrderFact]) -> Dict[int, dict]:
        buckets: Dict[int, dict] = {}
        for f in facts:
            if f.engineer_id <= 0:
                continue
            row = buckets.setdefault(
                f.engineer_id,
                {"engineer_id": f.engineer_id, "name": f.engineer_name, "orders": 0},
            )
            row["orders"] += 1
        return buckets

    def success_rates(self, facts: Iterable[EngineerRepairFact]) -> Dict[int, dict]:
        fact_list: List[EngineerRepairFact] = list(facts)
        buckets: Dict[int, dict] = {}
        for f in fact_list:
            if f.engineer_id <= 0:
                continue
            b = buckets.setdefault(
                f.engineer_id,
                {
                    "engineer_id": f.engineer_id,
                    "name": f.engineer_name,
                    "successful": 0,
                    "failed": 0,
                    "total": 0,
                    "avg_duration_hours": 0.0,
                },
            )
            b["total"] += 1
            status = (f.repair_status or "").lower()
            if status == "successful":
                b["successful"] += 1
            elif status == "failed":
                b["failed"] += 1
        for _, b in buckets.items():
            total = max(b["total"], 1)
            b["success_pct"] = round(100.0 * b["successful"] / total, 2)
            durations = [
                f.duration_hours
                for f in fact_list
                if f.engineer_id == b["engineer_id"] and f.duration_hours is not None
            ]
            b["avg_duration_hours"] = (
                round(sum(durations) / len(durations), 3) if durations else 0.0
            )
        return buckets

    def workload_index(self, orders_map: Dict[int, dict], repairs_map: Dict[int, dict]) -> List[dict]:
        """Simple composite workload score for ranking engineers."""
        ids = set(orders_map.keys()) | set(repairs_map.keys())
        out: List[dict] = []
        for eid in sorted(ids):
            o = orders_map.get(eid, {})
            r = repairs_map.get(eid, {})
            orders_n = int(o.get("orders", 0))
            repairs_n = int(r.get("total", 0))
            score = orders_n + 1.15 * repairs_n
            out.append(
                {
                    "engineer_id": eid,
                    "name": o.get("name") or r.get("name") or "",
                    "workload_score": round(score, 3),
                    "orders": orders_n,
                    "repairs": repairs_n,
                }
            )
        out.sort(key=lambda x: x["workload_score"], reverse=True)
        return out
