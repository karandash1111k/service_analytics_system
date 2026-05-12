"""Thin façade для импорта Excel через общий ETL pipeline."""

from __future__ import annotations

from pathlib import Path

from sqlalchemy.orm import Session

from etl.pipeline import ETLPipeline


class ExcelImportService:
    def __init__(self, session: Session) -> None:
        self._session = session

    def import_orders_workbook(self, path: str | Path) -> int:
        pipeline = ETLPipeline(self._session)
        result = pipeline.run_excel_orders(path)
        return result.rows_loaded
