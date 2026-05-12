"""Loads repair financial payloads originating from 1С."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from etl.extractor import OneCExtractor
from etl.loader import ETLLoader
from etl.transformer import ETLTransformer
from integrations.onec.onec_mapper import bundle_to_repairs
from models.integration_log import IntegrationLog
from models.sync_history import SyncHistory
from repositories.integration_log_repository import IntegrationLogRepository
from repositories.sync_history_repository import SyncHistoryRepository
from utils.logger import get_logger

logger = get_logger(__name__)


class OneCSyncService:
    SOURCE = "onec"

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
            batch = OneCExtractor().extract()
            mapped = bundle_to_repairs(batch.records)
            transformer = ETLTransformer()
            norm = transformer.transform_repairs(mapped)
            loader = ETLLoader(self._session)
            loaded = loader.load_repairs(norm)
            hist.records_processed = loaded
            hist.sync_status = "success"
            hist.finished_at = datetime.now(timezone.utc)
            self._history.update(hist)
            self._logs.add(
                IntegrationLog(
                    source_system=self.SOURCE,
                    operation_type="sync_repairs",
                    status="success",
                    message=f"processed_in={len(batch.records)}, loaded={loaded}",
                )
            )
            logger.info("1C sync finished, loaded=%s", loaded)
            return loaded
        except Exception as exc:
            logger.error("1C sync failed: %s", exc)
            hist.sync_status = "failed"
            hist.finished_at = datetime.now(timezone.utc)
            self._history.update(hist)
            self._logs.add(
                IntegrationLog(
                    source_system=self.SOURCE,
                    operation_type="sync_repairs",
                    status="failed",
                    message=str(exc),
                )
            )
            raise
