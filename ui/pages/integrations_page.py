"""Запуск интеграций и просмотр журналов синхронизации."""

from __future__ import annotations

from pathlib import Path

from PyQt6.QtWidgets import (
    QAbstractItemView,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from database.session import session_scope
from integrations.bitrix24.bitrix_sync import BitrixSyncService
from integrations.excel.excel_importer import ExcelImportService
from integrations.onec.onec_sync import OneCSyncService
from repositories.integration_log_repository import IntegrationLogRepository
from repositories.sync_history_repository import SyncHistoryRepository


class IntegrationsPage(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)

        header = QHBoxLayout()
        header.addWidget(QLabel("Интеграции и ETL"))
        header.addStretch(1)

        self._btn_bitrix = QPushButton("Синхронизация Bitrix24")
        self._btn_bitrix.setProperty("class", "action")
        self._btn_bitrix.clicked.connect(self._run_bitrix)

        self._btn_onec = QPushButton("Выгрузка из 1С")
        self._btn_onec.setProperty("class", "action")
        self._btn_onec.clicked.connect(self._run_onec)

        self._btn_excel = QPushButton("Импорт Excel")
        self._btn_excel.setProperty("class", "action")
        self._btn_excel.clicked.connect(self._run_excel_import)

        refresh = QPushButton("Обновить журналы")
        refresh.setProperty("class", "action")
        refresh.clicked.connect(self.refresh_tables)

        header.addWidget(self._btn_bitrix)
        header.addWidget(self._btn_onec)
        header.addWidget(self._btn_excel)
        header.addWidget(refresh)
        layout.addLayout(header)

        layout.addWidget(QLabel("Журнал интеграций"))
        self._logs_table = QTableWidget(0, 5)
        self._logs_table.setHorizontalHeaderLabels(
            ["ID", "Система", "Операция", "Статус", "Сообщение"]
        )
        self._logs_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self._logs_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        layout.addWidget(self._logs_table)

        layout.addWidget(QLabel("История синхронизаций"))
        self._sync_table = QTableWidget(0, 6)
        self._sync_table.setHorizontalHeaderLabels(
            ["ID", "Источник", "Обработано", "Начало", "Окончание", "Статус"]
        )
        self._sync_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self._sync_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        layout.addWidget(self._sync_table)

        self.refresh_tables()

    def refresh_tables(self) -> None:
        try:
            with session_scope() as session:
                logs = IntegrationLogRepository(session).list_recent(limit=150)
                self._logs_table.setRowCount(0)
                for log in logs:
                    row = self._logs_table.rowCount()
                    self._logs_table.insertRow(row)
                    values = [
                        str(log.id),
                        log.source_system,
                        log.operation_type,
                        log.status,
                        log.message[:240],
                    ]
                    for col, text in enumerate(values):
                        self._logs_table.setItem(row, col, QTableWidgetItem(text))

                hist = SyncHistoryRepository(session).list_recent(limit=80)
                self._sync_table.setRowCount(0)
                for h in hist:
                    row = self._sync_table.rowCount()
                    self._sync_table.insertRow(row)
                    vals = [
                        str(h.id),
                        h.source_system,
                        str(h.records_processed),
                        h.started_at.strftime("%Y-%m-%d %H:%M:%S"),
                        h.finished_at.strftime("%Y-%m-%d %H:%M:%S") if h.finished_at else "",
                        h.sync_status,
                    ]
                    for col, text in enumerate(vals):
                        self._sync_table.setItem(row, col, QTableWidgetItem(text))
        except Exception as exc:
            QMessageBox.critical(self, "Ошибка", f"Не удалось обновить журналы:\n{exc}")

    def _run_bitrix(self) -> None:
        try:
            with session_scope() as session:
                loaded = BitrixSyncService(session).run()
            QMessageBox.information(self, "Bitrix24", f"Загружено заявок: {loaded}")
            self.refresh_tables()
        except Exception as exc:
            QMessageBox.critical(self, "Bitrix24", str(exc))
            self.refresh_tables()

    def _run_onec(self) -> None:
        try:
            with session_scope() as session:
                loaded = OneCSyncService(session).run()
            QMessageBox.information(self, "1С", f"Загружено ремонтов: {loaded}")
            self.refresh_tables()
        except Exception as exc:
            QMessageBox.critical(self, "1С", str(exc))
            self.refresh_tables()

    def _run_excel_import(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите Excel файл заявок",
            str(Path.home()),
            "Excel (*.xlsx *.xls)",
        )
        if not path:
            return
        try:
            with session_scope() as session:
                loaded = ExcelImportService(session).import_orders_workbook(path)
            QMessageBox.information(self, "Excel", f"Импортировано строк: {loaded}")
            self.refresh_tables()
        except Exception as exc:
            QMessageBox.critical(self, "Excel", str(exc))
            self.refresh_tables()
