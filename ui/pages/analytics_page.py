"""Расширенная аналитика: SLA, ремонты, распределения."""

from __future__ import annotations

from PyQt6.QtWidgets import QHBoxLayout, QLabel, QMessageBox, QPushButton, QVBoxLayout, QWidget

from database.session import session_scope
from services.analytics_service import AnalyticsService
from ui.widgets.mpl_canvas import MatplotlibPanel


class AnalyticsPage(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)

        header = QHBoxLayout()
        header.addWidget(QLabel("Аналитика и KPI"))
        refresh = QPushButton("Обновить данные")
        refresh.setProperty("class", "action")
        refresh.clicked.connect(self.refresh)
        header.addStretch(1)
        header.addWidget(refresh)
        layout.addLayout(header)

        self._summary = QLabel()
        self._summary.setWordWrap(True)
        layout.addWidget(self._summary)

        charts = QHBoxLayout()
        self._plt_outcomes = MatplotlibPanel(figsize=(6.2, 3.8))
        self._plt_duration = MatplotlibPanel(figsize=(6.2, 3.8))
        charts.addWidget(self._plt_outcomes)
        charts.addWidget(self._plt_duration)
        layout.addLayout(charts)

        self._plt_sla_priority = MatplotlibPanel(figsize=(12.5, 3.6))
        layout.addWidget(self._plt_sla_priority)

        self.refresh()

    def refresh(self) -> None:
        try:
            with session_scope() as session:
                analytics = AnalyticsService(session)
                sla = analytics.sla_dashboard()
                rep = analytics.repair_dashboard()

                self._summary.setText(
                    "SLA: выполнено {sla_met}% • Просрочки {breach}% • "
                    "Ремонты: успех {succ}% • Средняя стоимость {cost} • Средняя длительность {dur} ч".format(
                        sla_met=sla.get("sla_met_pct", 0),
                        breach=sla.get("sla_breach_pct", 0),
                        succ=rep.get("success_pct", 0),
                        cost=rep.get("avg_cost", 0),
                        dur=rep.get("avg_duration_hours", 0),
                    )
                )

                outcomes = analytics.repairs_outcome_frame()
                dur_df = analytics.repair_duration_distribution()
                sla_pri = analytics.sla_breach_rate_by_priority_frame()

                fo = self._plt_outcomes.figure
                fo.clear()
                axo = fo.add_subplot(111)
                if outcomes.empty:
                    axo.text(0.5, 0.5, "Нет данных по статусам ремонтов", ha="center")
                    axo.axis("off")
                else:
                    axo.pie(outcomes["count"], labels=outcomes["status"], autopct="%1.1f%%")
                    axo.set_title("Структура статусов ремонтов")

                fd = self._plt_duration.figure
                fd.clear()
                axd = fd.add_subplot(111)
                if dur_df.empty:
                    axd.text(0.5, 0.5, "Нет данных по длительности", ha="center")
                    axd.axis("off")
                else:
                    bins = min(20, max(5, len(dur_df) // 3))
                    axd.hist(dur_df["duration_hours"], bins=bins, color="#059669")
                    axd.set_title("Распределение длительности ремонта (часы)")
                    axd.set_xlabel("Часы")

                fs = self._plt_sla_priority.figure
                fs.clear()
                axs = fs.add_subplot(111)
                if sla_pri.empty:
                    axs.text(0.5, 0.5, "Нет данных SLA по приоритетам", ha="center")
                    axs.axis("off")
                else:
                    axs.bar(sla_pri["priority"], sla_pri["breach_pct"], color="#dc2626")
                    axs.set_title("Доля SLA-нарушений по приоритетам заявок")
                    axs.set_ylabel("% просрочек")

                fo.tight_layout()
                fd.tight_layout()
                fs.tight_layout()
                self._plt_outcomes.redraw()
                self._plt_duration.redraw()
                self._plt_sla_priority.redraw()
        except Exception as exc:
            QMessageBox.critical(self, "Ошибка", f"Не удалось построить аналитику:\n{exc}")
