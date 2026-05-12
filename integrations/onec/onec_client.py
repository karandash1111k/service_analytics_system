"""
Mock 1С: OData/HTTP заменён офлайн JSON для корпоративной демонстрации.

Реальный контур может подменить `fetch_repairs_bundle` через наследование.
"""

from __future__ import annotations

import csv
import io
import json
from pathlib import Path
from typing import Any, List

from utils.logger import get_logger

logger = get_logger(__name__)

MOCK_JSON = """
[
  {
    "ORDER_REF": "1",
    "DEVICE": "Ноутбук",
    "MODEL": "Lenovo ThinkPad X1",
    "PROBLEM": "Нет изображения",
    "STATUS": "successful",
    "STARTED_AT": "2024-06-01 10:00:00",
    "FINISHED_AT": "2024-06-01 14:30:00",
    "COST": 12500.50
  },
  {
    "ORDER_REF": "2",
    "DEVICE": "Принтер",
    "MODEL": "HP LaserJet Pro",
    "PROBLEM": "Замятие бумаги",
    "STATUS": "failed",
    "STARTED_AT": "2024-06-02 09:15:00",
    "FINISHED_AT": "2024-06-02 11:00:00",
    "COST": 3200.00
  }
]
"""


class OneCMockClient:
    def fetch_repairs_bundle(self) -> List[dict[str, Any]]:
        base = Path(__file__).resolve().parent
        csv_path = base / "mock_repairs.csv"
        json_path = base / "mock_repairs.json"
        if json_path.exists():
            logger.info("1C mock: loading %s", json_path)
            return json.loads(json_path.read_text(encoding="utf-8"))
        if csv_path.exists():
            logger.info("1C mock: loading %s", csv_path)
            text = csv_path.read_text(encoding="utf-8")
            reader = csv.DictReader(io.StringIO(text))
            return [dict(row) for row in reader]
        logger.info("1C mock: embedded JSON bundle")
        return json.loads(MOCK_JSON)
