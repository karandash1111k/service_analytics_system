"""Excel workbook assembly using pandas + openpyxl."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import pandas as pd

if TYPE_CHECKING:
    from services.analytics_service import AnalyticsService


class ExcelAnalyticsReport:
    """Produces multi-sheet analytical workbook."""

    def __init__(self, analytics: "AnalyticsService") -> None:
        self._analytics = analytics

    def write(self, output_path: str | Path) -> Path:
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        summary = self._analytics.executive_summary()
        sla_df = pd.DataFrame([summary["sla"]])
        repairs_df = pd.DataFrame([summary["repairs"]])
        orders_day = self._analytics.orders_per_day_frame()
        workload = self._analytics.engineer_workload_frame()
        outcomes = self._analytics.repairs_outcome_frame()
        kpi_snap = self._analytics.latest_kpi_table()

        with pd.ExcelWriter(path, engine="openpyxl") as writer:
            pd.DataFrame(
                {
                    "metric": ["forecast_next_day_orders"],
                    "value": [summary["forecast_next_day_orders"]],
                }
            ).to_excel(writer, sheet_name="Executive", index=False)
            sla_df.to_excel(writer, sheet_name="SLA", index=False)
            repairs_df.to_excel(writer, sheet_name="Repairs", index=False)
            orders_day.to_excel(writer, sheet_name="OrdersPerDay", index=False)
            workload.to_excel(writer, sheet_name="EngineerWorkload", index=False)
            outcomes.to_excel(writer, sheet_name="RepairOutcomes", index=False)
            kpi_snap.to_excel(writer, sheet_name="KPISnapshot", index=False)
        return path
