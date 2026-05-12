"""Coordinates analytical exports — delegates to `reports` package."""

from __future__ import annotations

from pathlib import Path

from sqlalchemy.orm import Session

from reports.excel_report import ExcelAnalyticsReport
from reports.pdf_report import PdfAnalyticsReport
from services.analytics_service import AnalyticsService
from utils.logger import get_logger

logger = get_logger(__name__)


class ReportingService:
    def __init__(self, session: Session) -> None:
        self._analytics = AnalyticsService(session)

    def export_excel(self, output_path: str | Path) -> Path:
        try:
            report = ExcelAnalyticsReport(self._analytics)
            path = report.write(output_path)
            logger.info("Excel report written to %s", path)
            return path
        except Exception as exc:
            logger.error("Excel export failed: %s", exc)
            raise

    def export_pdf(self, output_path: str | Path) -> Path:
        try:
            report = PdfAnalyticsReport(self._analytics)
            path = report.write(output_path)
            logger.info("PDF report written to %s", path)
            return path
        except Exception as exc:
            logger.error("PDF export failed: %s", exc)
            raise
