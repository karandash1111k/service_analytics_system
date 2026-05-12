"""Просмотр ремонтов и фильтрация по статусу."""

from __future__ import annotations

from PyQt6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
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
from services.repair_service import RepairService


class RepairsPage(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)

        header = QHBoxLayout()
        header.addWidget(QLabel("Ремонты"))
        self._status = QComboBox()
        self._status.addItems(["", "pending", "in_progress", "successful", "failed", "cancelled"])
        refresh = QPushButton("Обновить")
        refresh.setProperty("class", "action")
        refresh.clicked.connect(self.refresh)
        header.addWidget(QLabel("Статус"))
        header.addWidget(self._status)
        header.addStretch(1)
        header.addWidget(refresh)
        layout.addLayout(header)

        self._table = QTableWidget(0, 9)
        self._table.setHorizontalHeaderLabels(
            [
                "ID",
                "Заявка",
                "Устройство",
                "Модель",
                "Статус",
                "Стоимость",
                "Начало",
                "Окончание",
                "Результат",
            ]
        )
        self._table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self._table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        layout.addWidget(self._table)
        self.refresh()

    def refresh(self) -> None:
        try:
            with session_scope() as session:
                status = self._status.currentText() or None
                repairs = RepairService(session).list_repairs(status=status)
                self._table.setRowCount(0)
                for repair in repairs:
                    row = self._table.rowCount()
                    self._table.insertRow(row)
                    values = [
                        str(repair.id),
                        str(repair.order_id),
                        repair.device_type,
                        repair.device_model,
                        repair.repair_status,
                        f"{repair.repair_cost:.2f}",
                        repair.started_at.strftime("%Y-%m-%d %H:%M") if repair.started_at else "",
                        repair.finished_at.strftime("%Y-%m-%d %H:%M") if repair.finished_at else "",
                        (repair.repair_result or "")[:120],
                    ]
                    for col, text in enumerate(values):
                        self._table.setItem(row, col, QTableWidgetItem(text))
        except Exception as exc:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить ремонты:\n{exc}")
