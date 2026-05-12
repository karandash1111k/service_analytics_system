"""Normalises 1С export keys prior to ETL transform."""

from __future__ import annotations

from typing import Any, Dict, List


def bundle_to_repairs(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Ensures transformer keys exist (`repair_status`, `device_type`, ...)."""
    out: List[Dict[str, Any]] = []
    for raw in rows:
        row = dict(raw)
        row.setdefault("repair_status", row.get("STATUS"))
        row.setdefault("device_type", row.get("DEVICE"))
        row.setdefault("device_model", row.get("MODEL"))
        row.setdefault("problem_description", row.get("PROBLEM"))
        row.setdefault("started_at", row.get("STARTED_AT"))
        row.setdefault("finished_at", row.get("FINISHED_AT"))
        row.setdefault("repair_cost", row.get("COST"))
        row.setdefault("order_ref", row.get("ORDER_REF"))
        out.append(row)
    return out
