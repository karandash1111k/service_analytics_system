"""Главное окно приложения — навигация и стек экранов."""

from __future__ import annotations

from PyQt6.QtCore import QSize
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from ui.pages.analytics_page import AnalyticsPage
from ui.pages.dashboard_page import DashboardPage
from ui.pages.integrations_page import IntegrationsPage
from ui.pages.orders_page import OrdersPage
from ui.pages.repairs_page import RepairsPage
from ui.pages.reports_page import ReportsPage
from ui.styles import APP_STYLESHEET


class MainWindow(QMainWindow):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Корпоративная аналитика выездного сервиса")
        self.resize(QSize(1280, 820))

        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(240)
        side_layout = QVBoxLayout(sidebar)
        brand = QLabel("SERVICE\nANALYTICS")
        brand.setStyleSheet("color:#f9fafb;font-weight:700;font-size:16px;padding:16px;")
        side_layout.addWidget(brand)

        self._stack = QStackedWidget()
        self._stack.setObjectName("contentStack")
        self._pages = {
            "dashboard": DashboardPage(),
            "orders": OrdersPage(),
            "repairs": RepairsPage(),
            "analytics": AnalyticsPage(),
            "integrations": IntegrationsPage(),
            "reports": ReportsPage(),
        }

        self._buttons: dict[str, QPushButton] = {}

        def add_nav(key: str, title: str) -> None:
            btn = QPushButton(title)
            btn.setCheckable(True)
            btn.setProperty("class", "nav")
            btn.clicked.connect(lambda checked=False, k=key: self._open_page(k))
            side_layout.addWidget(btn)
            self._buttons[key] = btn
            self._stack.addWidget(self._pages[key])

        add_nav("dashboard", "Дашборд")
        add_nav("orders", "Заявки")
        add_nav("repairs", "Ремонты")
        add_nav("analytics", "Аналитика")
        add_nav("integrations", "Интеграции")
        add_nav("reports", "Отчёты")

        side_layout.addStretch(1)

        layout.addWidget(sidebar)
        layout.addWidget(self._stack, stretch=1)

        self.setCentralWidget(container)

        self._apply_exclusive_nav("dashboard")
        try:
            self._pages["dashboard"].refresh()
        except Exception as exc:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить дашборд:\n{exc}")

    def _apply_exclusive_nav(self, active_key: str) -> None:
        for key, btn in self._buttons.items():
            btn.setChecked(key == active_key)

    def _open_page(self, key: str) -> None:
        try:
            self._apply_exclusive_nav(key)
            mapping = {
                "dashboard": 0,
                "orders": 1,
                "repairs": 2,
                "analytics": 3,
                "integrations": 4,
                "reports": 5,
            }
            self._stack.setCurrentIndex(mapping[key])
            page = self._pages[key]
            if hasattr(page, "refresh"):
                page.refresh()
        except Exception as exc:
            QMessageBox.critical(self, "Ошибка", str(exc))

def apply_theme(app) -> None:
    app.setStyle("Fusion")
    app.setStyleSheet(APP_STYLESHEET)
