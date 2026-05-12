"""Excel analytics export — thin wrapper over reporting service."""

from __future__ import annotations

from pathlib import Path

from sqlalchemy.orm import Session

from services.reporting_service import ReportingService


class ExcelAnalyticsExporter:
    def __init__(self, session: Session) -> None:
        self._reporting = ReportingService(session)

    def export(self, output_path: str | Path) -> Path:
        return self._reporting.export_excel(output_path)
