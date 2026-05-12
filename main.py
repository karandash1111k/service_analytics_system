"""
Точка входа desktop-приложения аналитики сервисной организации.

Запуск (из каталога `service_analytics_system`):

    python main.py
"""

from __future__ import annotations

import logging
import sys

from PyQt6.QtWidgets import QApplication

from sqlalchemy.exc import OperationalError

from config.settings import get_settings
from database.connection import create_engine_from_settings, dispose_engine
from database.schema import create_all_tables
from database.session import configure_session_factory
from ui.main_window import MainWindow, apply_theme
from utils.logger import get_logger, setup_logging


logger = get_logger(__name__)


def bootstrap_infrastructure() -> None:
    """Подключение к MySQL, создание таблиц при необходимости."""
    settings = get_settings()
    setup_logging(settings.app_log_level)
    engine = create_engine_from_settings(settings)
    create_all_tables(engine)
    configure_session_factory()
    logger.info("Инфраструктура БД готова: %s", settings.db_name)


def main() -> int:
    try:
        bootstrap_infrastructure()
    except OperationalError as exc:
        logging.basicConfig(level=logging.ERROR)
        logging.exception("Не удалось инициализировать базу данных: %s", exc)
        if exc.orig and getattr(exc.orig, "args", None) and exc.orig.args[0] == 1045:
            logging.error(
                "Отказ MySQL в доступе: проверьте DB_USER и DB_PASSWORD в `.env` "
                "(пароль не должен оставаться примером из шаблона)."
            )
        return 1
    except Exception as exc:
        logging.basicConfig(level=logging.ERROR)
        logging.exception("Не удалось инициализировать базу данных: %s", exc)
        return 1

    app = QApplication(sys.argv)
    apply_theme(app)
    window = MainWindow()

    def handle_exception(exc_type, exc, tb) -> None:
        logger.error("Необработанное исключение UI", exc_info=(exc_type, exc, tb))

    sys.excepthook = handle_exception

    window.show()
    code = app.exec()
    dispose_engine()
    return int(code)


if __name__ == "__main__":
    sys.exit(main())
