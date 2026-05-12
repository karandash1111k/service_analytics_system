"""
Bitrix24 REST façade — mock-first для офлайн-демонстраций.

При наличии `BITRIX_WEBHOOK_URL` выполняется реальный HTTP вызов (опционально).
"""

from __future__ import annotations

import json
import os
from typing import Any, List

import requests

from utils.logger import get_logger

logger = get_logger(__name__)


MOCK_DEALS_JSON = """
[
  {
    "ID": "BX-1001",
    "TITLE": "Не включается ноутбук Dell",
    "COMMENTS": "Клиент просит срочный выезд",
    "PRIORITY": "high",
    "STAGE_ID": "assigned",
    "CONTACT": {"NAME": "Иван Петров", "PHONE": "+79990001122", "EMAIL": "ivan.p@corp.demo"}
  },
  {
    "ID": "BX-1002",
    "TITLE": "Замена матрицы моноблока",
    "COMMENTS": "",
    "PRIORITY": "medium",
    "STAGE_ID": "in progress",
    "CONTACT": {"NAME": "ООО ТехноЛайн", "PHONE": "+74951234567", "EMAIL": "svc@technoline.demo"}
  },
  {
    "ID": "BX-1003",
    "TITLE": "Диагностика ИБП",
    "COMMENTS": "Объект: склад №4",
    "PRIORITY": "low",
    "STAGE_ID": "new",
    "CONTACT": {"NAME": "Светлана Орлова", "PHONE": "+79887776655", "EMAIL": "orlova@mail.demo"}
  }
]
"""


class BitrixMockClient:
    """Имитация CRM.deal.list — возвращает структурированный JSON."""

    def __init__(self, webhook_url: str | None = None) -> None:
        self._webhook = webhook_url or os.getenv("BITRIX_WEBHOOK_URL")

    def fetch_service_orders(self) -> List[dict[str, Any]]:
        if self._webhook:
            try:
                url = self._webhook.rstrip("/") + "/crm.deal.list"
                resp = requests.get(url, timeout=15)
                resp.raise_for_status()
                payload = resp.json()
                return payload.get("result", payload)
            except Exception as exc:
                logger.error("Bitrix REST failure, fallback to mock: %s", exc)
        return json.loads(MOCK_DEALS_JSON)
