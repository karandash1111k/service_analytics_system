"""
Transform stage — cleansing, normalisation, derived metrics.

Keeps enterprise conventions for statuses and validates mandatory keys.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Iterable, List

from etl.extractor import ExtractSource
from utils.constants import (
    ORDER_STATUS_NORMALISED,
    REPAIR_STATUS_NORMALISED,
    SLA_HOURS_BY_PRIORITY,
)
from utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class NormalisedOrderRow:
    external_id: str
    title: str
    description: str
    priority: str
    status: str
    client_name: str
    client_phone: str
    client_email: str


@dataclass
class NormalisedRepairRow:
    external_order_ref: str
    device_type: str
    device_model: str
    problem_description: str
    repair_status: str
    started_at: datetime | None
    finished_at: datetime | None
    repair_cost: float


class ETLTransformer:
    """Stateful-less transforms suitable for unit testing."""

    ORDER_STATUS_MAP = {
        "new": "new",
        "assigned": "assigned",
        "in progress": "in_progress",
        "in_progress": "in_progress",
        "completed": "completed",
        "done": "completed",
        "cancel": "cancelled",
        "cancelled": "cancelled",
    }

    REPAIR_STATUS_MAP = {
        "pending": "pending",
        "work": "in_progress",
        "in progress": "in_progress",
        "success": "successful",
        "successful": "successful",
        "fail": "failed",
        "failed": "failed",
    }

    def transform_orders(self, source: ExtractSource, rows: Iterable[dict]) -> List[NormalisedOrderRow]:
        out: List[NormalisedOrderRow] = []
        for raw in rows:
            try:
                norm = self._normalise_order(raw, source)
                self._validate_order(norm)
                out.append(norm)
            except Exception as exc:
                logger.warning("Order row skipped: %s | raw=%s", exc, raw)
        return out

    def transform_repairs(self, rows: Iterable[dict]) -> List[NormalisedRepairRow]:
        out: List[NormalisedRepairRow] = []
        for raw in rows:
            try:
                norm = self._normalise_repair(raw)
                self._validate_repair(norm)
                out.append(norm)
            except Exception as exc:
                logger.warning("Repair row skipped: %s | raw=%s", exc, raw)
        return out

    def derive_duration_hours(self, start: datetime | None, end: datetime | None) -> float | None:
        if start is None or end is None:
            return None
        return max((end - start).total_seconds() / 3600.0, 0.0)

    def _normalise_order(self, raw: dict, source: ExtractSource) -> NormalisedOrderRow:
        if source == ExtractSource.BITRIX24:
            ext_id = str(raw.get("ID"))
            title = str(raw.get("TITLE", "")).strip()
            description = str(raw.get("COMMENTS", "")).strip()
            priority = str(raw.get("PRIORITY", "medium")).lower()
            status_raw = str(raw.get("STAGE_ID", "new")).lower()
            contact = raw.get("CONTACT", {}) if isinstance(raw.get("CONTACT"), dict) else {}
            client_name = str(contact.get("NAME", "")).strip()
            client_phone = str(contact.get("PHONE", "")).strip()
            client_email = str(contact.get("EMAIL", "")).strip()
        elif source == ExtractSource.EXCEL:
            ext_id = str(raw.get("external_id") or raw.get("order_id"))
            title = str(raw.get("title", "")).strip()
            description = str(raw.get("description", "")).strip()
            priority = str(raw.get("priority", "medium")).lower()
            status_raw = str(raw.get("status", "new")).lower()
            client_name = str(raw.get("client_name", "")).strip()
            client_phone = str(raw.get("client_phone", "")).strip()
            client_email = str(raw.get("client_email", "")).strip()
        else:
            raise ValueError(f"Unsupported source for orders: {source}")

        status = self.ORDER_STATUS_MAP.get(status_raw, status_raw.replace(" ", "_"))
        if status not in ORDER_STATUS_NORMALISED:
            status = "new"

        return NormalisedOrderRow(
            external_id=ext_id,
            title=title or f"Import {ext_id}",
            description=description,
            priority=priority if priority in SLA_HOURS_BY_PRIORITY else "medium",
            status=status,
            client_name=client_name or "Импортированный клиент",
            client_phone=client_phone or "000",
            client_email=client_email or "import@example.com",
        )

    def _normalise_repair(self, raw: dict) -> NormalisedRepairRow:
        status_raw = str(raw.get("repair_status") or raw.get("STATUS", "")).lower()
        status = self.REPAIR_STATUS_MAP.get(status_raw, status_raw.replace(" ", "_"))
        if status not in REPAIR_STATUS_NORMALISED:
            status = "pending"

        started = raw.get("started_at") or raw.get("STARTED_AT")
        finished = raw.get("finished_at") or raw.get("FINISHED_AT")

        def parse_dt(val: Any) -> datetime | None:
            if val is None or (isinstance(val, float) and str(val) == "nan"):
                return None
            if isinstance(val, datetime):
                return val
            text = str(val).strip()
            if not text:
                return None
            for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"):
                try:
                    return datetime.strptime(text.replace("Z", ""), fmt)
                except ValueError:
                    continue
            return None

        cost_raw = raw.get("repair_cost") or raw.get("COST") or 0
        try:
            repair_cost = float(cost_raw)
        except (TypeError, ValueError):
            repair_cost = 0.0

        return NormalisedRepairRow(
            external_order_ref=str(raw.get("order_ref") or raw.get("ORDER_REF")),
            device_type=str(raw.get("device_type") or raw.get("DEVICE", "")).strip(),
            device_model=str(raw.get("device_model") or raw.get("MODEL", "")).strip(),
            problem_description=str(raw.get("problem_description") or raw.get("PROBLEM", "")).strip(),
            repair_status=status,
            started_at=parse_dt(started),
            finished_at=parse_dt(finished),
            repair_cost=repair_cost,
        )

    def _validate_order(self, row: NormalisedOrderRow) -> None:
        if not row.external_id:
            raise ValueError("external_id required")

    def _validate_repair(self, row: NormalisedRepairRow) -> None:
        if not row.external_order_ref:
            raise ValueError("order ref required")
        if not row.device_type:
            raise ValueError("device type required")
