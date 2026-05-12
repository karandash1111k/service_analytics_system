"""
Extract stage — pulls raw artefacts from enterprise sources.

Bitrix24 / 1С use mocked payloads suitable for offline demos.
Excel path delegates to pandas ingestion.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, List

import pandas as pd

from integrations.bitrix24.bitrix_client import BitrixMockClient
from integrations.onec.onec_client import OneCMockClient
from utils.logger import get_logger

logger = get_logger(__name__)


class ExtractSource(str, Enum):
    BITRIX24 = "bitrix24"
    ONEC = "onec"
    EXCEL = "excel"


@dataclass
class RawBatch:
    source: ExtractSource
    records: List[dict[str, Any]]


class BitrixExtractor:
    def __init__(self, client: BitrixMockClient | None = None) -> None:
        self._client = client or BitrixMockClient()

    def extract(self) -> RawBatch:
        payload = self._client.fetch_service_orders()
        logger.info("Bitrix extract: %s raw deals", len(payload))
        return RawBatch(source=ExtractSource.BITRIX24, records=payload)


class OneCExtractor:
    def __init__(self, client: OneCMockClient | None = None) -> None:
        self._client = client or OneCMockClient()

    def extract(self) -> RawBatch:
        payload = self._client.fetch_repairs_bundle()
        logger.info("1C extract: %s repair bundles", len(payload))
        return RawBatch(source=ExtractSource.ONEC, records=payload)


class ExcelExtractor:
    def __init__(self, file_path: str | Path) -> None:
        self._path = Path(file_path)

    def extract(self) -> RawBatch:
        df = pd.read_excel(self._path)
        records = df.to_dict(orient="records")
        logger.info("Excel extract: %s rows from %s", len(records), self._path)
        return RawBatch(source=ExtractSource.EXCEL, records=records)
