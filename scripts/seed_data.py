"""
Заполнение БД демонстрационными данными.

Запуск из корня пакета:
    python scripts/seed_data.py

Требуется созданная схема MySQL и файл `.env` с параметрами подключения.
"""

from __future__ import annotations

import random
import sys
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from config.settings import get_settings  # noqa: E402
from database.connection import create_engine_from_settings, dispose_engine  # noqa: E402
from database.schema import create_all_tables  # noqa: E402
from database.session import configure_session_factory, session_scope  # noqa: E402
from models.client import Client  # noqa: E402
from models.engineer import Engineer  # noqa: E402
from models.kpi_metric import KPIMetric  # noqa: E402
from models.repair import Repair  # noqa: E402
from models.service_order import ServiceOrder  # noqa: E402
from models.spare_part import SparePart  # noqa: E402
from repositories.client_repository import ClientRepository  # noqa: E402
from repositories.engineer_repository import EngineerRepository  # noqa: E402
from repositories.order_repository import OrderRepository  # noqa: E402
from repositories.repair_repository import RepairRepository  # noqa: E402
from repositories.spare_part_repository import SparePartRepository  # noqa: E402
from repositories.kpi_repository import KPIRepository  # noqa: E402
from services.kpi_service import KPIService  # noqa: E402
from utils.logger import get_logger, setup_logging  # noqa: E402


logger = get_logger(__name__)

CLIENT_NAMES = [
    "АО КвантСервис",
    "ИП Сидоров А.В.",
    "ООО ЛогистикПро",
    "ЗАО ТехноРегион",
    "ТД АльфаЭлектро",
    "МУП ГорСвет",
    "ООО Платформа",
    "ИП Кузнецова Е.Н.",
    "ООО РемСити",
    "Холдинг Дельта",
    "ТСЖ Речной",
    "ООО ИнтеграКом",
    "Фонд Развития",
    "Магазин Цифра",
    "ООО НоваЛайн",
    "Кафе Центральное",
    "Школа №42",
    "Банк Партнёр",
    "ООО Спектр",
    "Клиника Вита",
]

ENGINEERS = [
    ("Алексей Воронов", "notebook", "+79161001001", "voronov@corp.demo"),
    ("Мария Ким", "printer", "+79161001002", "kim@corp.demo"),
    ("Денис Орлов", "ups", "+79161001003", "orlov@corp.demo"),
    ("Екатерина Жукова", "network", "+79161001004", "zhukova@corp.demo"),
    ("Игорь Сабитов", "server", "+79161001005", "sabitov@corp.demo"),
    ("Ольга Лебедева", "notebook", "+79161001006", "lebedeva@corp.demo"),
    ("Павел Никитин", "printer", "+79161001007", "nikitin@corp.demo"),
    ("Антон Громов", "electronics", "+79161001008", "gromov@corp.demo"),
    ("Светлана Рыжова", "notebook", "+79161001009", "ryzhova@corp.demo"),
    ("Виктор Хан", "server", "+79161001010", "khan@corp.demo"),
]

DEVICE_POOL = [
    ("Ноутбук", "Dell Latitude 5540"),
    ("Ноутбук", "Lenovo ThinkPad T14"),
    ("Принтер", "HP LaserJet Pro M404dn"),
    ("МФУ", "Canon imageRUNNER C3226"),
    ("ИБП", "APC Smart-UPS 1500"),
    ("Сервер", "Dell PowerEdge R650"),
    ("Монитор", "LG 27UL850"),
    ("ПК", "HP EliteDesk 800"),
]


def _seed_rng() -> random.Random:
    rnd = random.Random(42)
    return rnd


def bootstrap_schema() -> None:
    settings = get_settings()
    setup_logging(settings.app_log_level)
    logger.info(
        "Подключение seed: %s@%s:%s/%s — должно совпадать с `.env` при запуске приложения.",
        settings.db_user,
        settings.db_host,
        settings.db_port,
        settings.db_name,
    )
    engine = create_engine_from_settings(settings)
    create_all_tables(engine)
    configure_session_factory()
    logger.info("Схема проверена / создана.")


def seed_sample_payload() -> None:
    rnd = _seed_rng()
    bootstrap_schema()

    now = datetime.now(timezone.utc)
    priorities = ["low", "medium", "high", "critical"]
    order_statuses_weighted = (
        ["new"] * 5
        + ["assigned"] * 10
        + ["in_progress"] * 15
        + ["completed"] * 55
        + ["cancelled"] * 5
    )
    repair_statuses_weighted = (
        ["successful"] * 65 + ["failed"] * 10 + ["pending"] * 10 + ["in_progress"] * 15
    )

    with session_scope() as session:
        crepo = ClientRepository(session)
        erepo = EngineerRepository(session)
        orepo = OrderRepository(session)
        rrepo = RepairRepository(session)
        prepo = SparePartRepository(session)
        krepo = KPIRepository(session)

        clients: list[Client] = []
        for idx, name in enumerate(CLIENT_NAMES):
            c = Client(
                full_name=name,
                phone=f"+7495{1000000 + idx}",
                email=f"client{idx + 1}@demo.corp",
                address=f"г. Москва, ул. Примерная, д. {idx + 1}",
            )
            clients.append(crepo.add(c))

        engineers: list[Engineer] = []
        for full_name, spec, phone, email in ENGINEERS:
            hire = now.date() - timedelta(days=rnd.randint(200, 1400))
            eng = Engineer(
                full_name=full_name,
                specialization=spec,
                phone=phone,
                email=email,
                hire_date=hire,
                status="active",
            )
            engineers.append(erepo.add(eng))

        parts: list[SparePart] = []
        for i in range(18):
            p = SparePart(
                name=f"Запчасть #{i + 1}",
                part_number=f"PN-{1000 + i}",
                quantity=rnd.randint(5, 120),
                price=Decimal(str(round(rnd.uniform(800, 25000), 2))),
            )
            parts.append(prepo.add(p))

        orders: list[ServiceOrder] = []
        for i in range(58):
            client = rnd.choice(clients)
            engineer = rnd.choice(engineers)
            created = now - timedelta(days=rnd.randint(0, 180), hours=rnd.randint(0, 23))
            status = rnd.choice(order_statuses_weighted)
            assigned_at = None
            completed_at = None
            eng_id = engineer.id

            if status == "new":
                eng_id = None if rnd.random() < 0.4 else engineer.id
                assigned_at = created + timedelta(hours=rnd.randint(1, 36)) if eng_id else None
            elif status == "assigned":
                assigned_at = created + timedelta(hours=rnd.randint(1, 24))
            elif status in {"in_progress", "completed", "cancelled"}:
                assigned_at = created + timedelta(hours=rnd.randint(1, 12))
                if status == "completed":
                    completed_at = assigned_at + timedelta(hours=rnd.randint(6, 96))
                elif status == "cancelled":
                    completed_at = assigned_at + timedelta(hours=rnd.randint(2, 48))

            order = ServiceOrder(
                client_id=client.id,
                engineer_id=eng_id,
                title=f"Заявка #{i + 1}: обслуживание оборудования",
                description="Диагностика и восстановление работоспособности.",
                status=status,
                priority=rnd.choice(priorities),
                created_at=created,
                assigned_at=assigned_at,
                completed_at=completed_at,
            )
            orders.append(orepo.add(order))

        for order in orders:
            if rnd.random() < 0.82:
                dtype, dmodel = rnd.choice(DEVICE_POOL)
                rstat = rnd.choice(repair_statuses_weighted)
                start = (
                    (order.assigned_at or order.created_at)
                    + timedelta(hours=rnd.randint(1, 18))
                )
                finish = None
                if rstat in {"successful", "failed"}:
                    finish = start + timedelta(hours=rnd.uniform(2, 36))
                cost = Decimal(str(round(rnd.uniform(1500, 55000), 2)))
                repair = Repair(
                    order_id=order.id,
                    device_type=dtype,
                    device_model=dmodel,
                    problem_description="Неисправность узла / программный сбой.",
                    repair_result="Успешный ремонт" if rstat == "successful" else None,
                    repair_status=rstat,
                    started_at=start,
                    finished_at=finish,
                    repair_cost=cost,
                )
                rep = rrepo.add(repair)
                if rnd.random() < 0.45:
                    used = rnd.sample(parts, k=min(3, len(parts)))
                    for sp in used:
                        if sp not in rep.spare_parts:
                            rep.spare_parts.append(sp)

        hist_metrics = []
        for eng in engineers:
            hist_metrics.append(
                KPIMetric(
                    engineer_id=eng.id,
                    metric_name="historical_orders",
                    metric_value=Decimal(str(rnd.randint(15, 120))),
                    calculated_at=now - timedelta(days=30),
                )
            )
        krepo.add_many(hist_metrics)

        logger.info("Базовые записи загружены — расчёт KPI...")
        KPIService(session).snapshot_engineer_kpis()

    logger.info("Seed завершён: клиенты=%s, инженеры=%s, заявки=%s", len(CLIENT_NAMES), len(ENGINEERS), 58)


def main() -> None:
    try:
        seed_sample_payload()
    finally:
        dispose_engine()


if __name__ == "__main__":
    main()
