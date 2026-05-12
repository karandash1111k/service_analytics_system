"""Экспорт отчётов в Excel и PDF."""

from __future__ import annotations

from pathlib import Path

from PyQt6.QtWidgets import QFileDialog, QHBoxLayout, QLabel, QMessageBox, QPushButton, QVBoxLayout, QWidget

from database.session import session_scope
from services.reporting_service import ReportingService


class ReportsPage(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Отчёты для руководства"))
        layout.addWidget(
            QLabel(
                "Формируются сводные листы KPI, SLA, загрузки инженеров и приложения с графиками "
                "(PDF)."
            )
        )

        row = QHBoxLayout()
        excel_btn = QPushButton("Экспорт Excel…")
        excel_btn.setProperty("class", "action")
        excel_btn.clicked.connect(self._export_excel)

        pdf_btn = QPushButton("Экспорт PDF…")
        pdf_btn.setProperty("class", "action")
        pdf_btn.clicked.connect(self._export_pdf)

        row.addWidget(excel_btn)
        row.addWidget(pdf_btn)
        row.addStretch(1)
        layout.addLayout(row)
        layout.addStretch(1)

    def _export_excel(self) -> None:
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Сохранить Excel отчёт",
            str(Path.home() / "service_analytics_report.xlsx"),
            "Excel (*.xlsx)",
        )
        if not path:
            return
        try:
            with session_scope() as session:
                ReportingService(session).export_excel(path)
            QMessageBox.information(self, "Готово", f"Файл сохранён:\n{path}")
        except Exception as exc:
            QMessageBox.critical(self, "Ошибка экспорта", str(exc))

    def _export_pdf(self) -> None:
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Сохранить PDF отчёт",
            str(Path.home() / "service_analytics_report.pdf"),
            "PDF (*.pdf)",
        )
        if not path:
            return
        try:
            with session_scope() as session:
                ReportingService(session).export_pdf(path)
            QMessageBox.information(self, "Готово", f"Файл сохранён:\n{path}")
        except Exception as exc:
            QMessageBox.critical(self, "Ошибка экспорта", str(exc))
