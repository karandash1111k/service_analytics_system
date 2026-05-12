"""Управление заявками: таблица, фильтрация, назначение инженера."""

from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from database.session import session_scope
from repositories.engineer_repository import EngineerRepository
from services.order_service import OrderService


class OrdersPage(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)

        header = QHBoxLayout()
        header.addWidget(QLabel("Заявки"))
        self._status_filter = QComboBox()
        self._status_filter.addItems(
            ["", "new", "assigned", "in_progress", "completed", "cancelled"]
        )
        self._search = QLineEdit()
        self._search.setPlaceholderText("Поиск по названию / описанию…")

        refresh_btn = QPushButton("Обновить")
        refresh_btn.setProperty("class", "action")
        refresh_btn.clicked.connect(self.refresh)

        assign_btn = QPushButton("Назначить инженера")
        assign_btn.setProperty("class", "action")
        assign_btn.clicked.connect(self._assign_selected)

        complete_btn = QPushButton("Завершить")
        complete_btn.setProperty("class", "action")
        complete_btn.clicked.connect(self._complete_selected)

        header.addWidget(QLabel("Статус"))
        header.addWidget(self._status_filter)
        header.addWidget(self._search, stretch=1)
        header.addWidget(refresh_btn)
        header.addWidget(assign_btn)
        header.addWidget(complete_btn)
        layout.addLayout(header)

        self._engineers = QComboBox()
        layout.addWidget(self._engineers)

        self._table = QTableWidget(0, 8)
        self._table.setHorizontalHeaderLabels(
            ["ID", "Клиент", "Инженер", "Заголовок", "Статус", "Приоритет", "Создана", "Завершена"]
        )
        self._table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self._table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self._table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        layout.addWidget(self._table)

        self.refresh(init_engineers=True)

    def refresh(self, init_engineers: bool = False) -> None:
        try:
            with session_scope() as session:
                if init_engineers:
                    self._engineers.clear()
                    engineers = EngineerRepository(session).list_active()
                    for eng in engineers:
                        self._engineers.addItem(eng.full_name, eng.id)

                svc = OrderService(session)
                status = self._status_filter.currentText() or None
                search = self._search.text().strip() or None
                orders = svc.list_orders(status=status, search=search)

                self._table.setRowCount(0)
                for order in orders:
                    row = self._table.rowCount()
                    self._table.insertRow(row)
                    items = [
                        str(order.id),
                        order.client.full_name if order.client else "",
                        order.engineer.full_name if order.engineer else "",
                        order.title,
                        order.status,
                        order.priority,
                        order.created_at.strftime("%Y-%m-%d %H:%M"),
                        order.completed_at.strftime("%Y-%m-%d %H:%M") if order.completed_at else "",
                    ]
                    for col, text in enumerate(items):
                        cell = QTableWidgetItem(text)
                        if col == 0:
                            cell.setData(Qt.ItemDataRole.UserRole, order.id)
                        self._table.setItem(row, col, cell)
        except Exception as exc:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить заявки:\n{exc}")

    def _selected_order_id(self) -> int | None:
        rows = self._table.selectionModel().selectedRows()
        if not rows:
            QMessageBox.warning(self, "Выбор", "Выберите строку заявки.")
            return None
        item = self._table.item(rows[0].row(), 0)
        if item is None:
            return None
        val = item.data(Qt.ItemDataRole.UserRole)
        return int(val) if val is not None else None

    def _assign_selected(self) -> None:
        order_id = self._selected_order_id()
        if order_id is None:
            return
        engineer_id = self._engineers.currentData()
        if engineer_id is None:
            QMessageBox.warning(self, "Инженер", "Выберите инженера из списка.")
            return
        try:
            with session_scope() as session:
                OrderService(session).assign_engineer(order_id, int(engineer_id))
            self.refresh()
            QMessageBox.information(self, "Готово", "Инженер назначен.")
        except Exception as exc:
            QMessageBox.critical(self, "Ошибка", str(exc))

    def _complete_selected(self) -> None:
        order_id = self._selected_order_id()
        if order_id is None:
            return
        try:
            with session_scope() as session:
                OrderService(session).mark_completed(order_id)
            self.refresh()
            QMessageBox.information(self, "Готово", "Заявка отмечена как завершённая.")
        except Exception as exc:
            QMessageBox.critical(self, "Ошибка", str(exc))
