"""Synchronises Bitrix CRM artefacts through the ETL pipeline."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from etl.pipeline import ETLPipeline
from models.integration_log import IntegrationLog
from models.sync_history import SyncHistory
from repositories.integration_log_repository import IntegrationLogRepository
from repositories.sync_history_repository import SyncHistoryRepository
from utils.logger import get_logger

logger = get_logger(__name__)


class BitrixSyncService:
    SOURCE = "bitrix24"

    def __init__(self, session: Session) -> None:
        self._session = session
        self._history = SyncHistoryRepository(session)
        self._logs = IntegrationLogRepository(session)

    def run(self) -> int:
        started = datetime.now(timezone.utc)
        hist = SyncHistory(
            source_system=self.SOURCE,
            records_processed=0,
            started_at=started,
            finished_at=None,
            sync_status="running",
        )
        self._history.add(hist)
        self._session.flush()

        try:
            pipeline = ETLPipeline(self._session)
            result = pipeline.run_bitrix_orders()
            hist.records_processed = result.rows_loaded
            hist.sync_status = "success"
            hist.finished_at = datetime.now(timezone.utc)
            self._history.update(hist)
            self._logs.add(
                IntegrationLog(
                    source_system=self.SOURCE,
                    operation_type="sync_orders",
                    status="success",
                    message=f"processed_in={result.rows_in}, loaded={result.rows_loaded}",
                )
            )
            logger.info("Bitrix sync finished: %s", result)
            return result.rows_loaded
        except Exception as exc:
            logger.error("Bitrix sync failed: %s", exc)
            hist.sync_status = "failed"
            hist.finished_at = datetime.now(timezone.utc)
            self._history.update(hist)
            self._logs.add(
                IntegrationLog(
                    source_system=self.SOURCE,
                    operation_type="sync_orders",
                    status="failed",
                    message=str(exc),
                )
            )
            raise
