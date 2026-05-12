"""Генерация примера Excel для импорта заявок через ETL → Loader."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def main() -> None:
    rows = [
        {
            "external_id": "IMP-501",
            "title": "Импорт: диагностика UPS",
            "description": "Пропадает питание при переключении на батарею.",
            "priority": "high",
            "status": "new",
            "client_name": "Лаборатория Альфа",
            "client_phone": "+74957778899",
            "client_email": "lab-alpha@import.demo",
        },
        {
            "external_id": "IMP-502",
            "title": "Импорт: настройка МФУ",
            "description": "Подключение к домену и сканирование в SMB.",
            "priority": "medium",
            "status": "assigned",
            "client_name": "ООО Документ",
            "client_phone": "+78123334455",
            "client_email": "office@docs.demo",
        },
    ]
    path = ROOT / "sample_orders_import.xlsx"
    pd.DataFrame(rows).to_excel(path, index=False)
    print(f"Создан файл: {path}")


if __name__ == "__main__":
    main()
