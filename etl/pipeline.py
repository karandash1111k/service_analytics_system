"""Orchestrates Extract → Transform → Load with observability hooks."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from sqlalchemy.orm import Session

from etl.extractor import BitrixExtractor, ExcelExtractor, ExtractSource, OneCExtractor, RawBatch
from etl.loader import ETLLoader
from etl.transformer import ETLTransformer
from models.integration_log import IntegrationLog
from repositories.integration_log_repository import IntegrationLogRepository
from utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class PipelineResult:
    source: ExtractSource
    rows_in: int
    rows_loaded: int


class ETLPipeline:
    def __init__(self, session: Session) -> None:
        self._session = session
        self._transformer = ETLTransformer()
        self._loader = ETLLoader(session)
        self._logs = IntegrationLogRepository(session)

    def run_bitrix_orders(self) -> PipelineResult:
        batch = BitrixExtractor().extract()
        norm = self._transformer.transform_orders(batch.source, batch.records)
        loaded = self._loader.load_orders(norm)
        self._log_etl(batch.source.value, "orders_etl", "success", f"loaded={loaded}")
        return PipelineResult(batch.source, len(batch.records), loaded)

    def run_onec_repairs(self) -> PipelineResult:
        batch = OneCExtractor().extract()
        norm = self._transformer.transform_repairs(batch.records)
        loaded = self._loader.load_repairs(norm)
        self._log_etl(batch.source.value, "repairs_etl", "success", f"loaded={loaded}")
        return PipelineResult(batch.source, len(batch.records), loaded)

    def run_excel_orders(self, path: str | Path) -> PipelineResult:
        batch = ExcelExtractor(path).extract()
        norm = self._transformer.transform_orders(batch.source, batch.records)
        loaded = self._loader.load_orders(norm)
        self._log_etl(batch.source.value, "excel_orders", "success", f"loaded={loaded}")
        return PipelineResult(batch.source, len(batch.records), loaded)

    def _log_etl(self, source: str, op: str, status: str, message: str) -> None:
        try:
            self._logs.add(
                IntegrationLog(
                    source_system=source,
                    operation_type=op,
                    status=status,
                    message=message,
                )
            )
            self._session.flush()
        except Exception as exc:
            logger.error("Failed to persist integration log: %s", exc)
