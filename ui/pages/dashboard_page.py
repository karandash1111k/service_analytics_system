"""Executive dashboard — KPI cards и ключевые графики."""

from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QGridLayout, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from database.session import session_scope
from services.analytics_service import AnalyticsService
from ui.widgets.mpl_canvas import MatplotlibPanel


class DashboardPage(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        root = QVBoxLayout(self)

        title = QLabel("Пульт управления сервисом")
        title.setObjectName("title")
        root.addWidget(title, alignment=Qt.AlignmentFlag.AlignLeft)

        self._cards = QHBoxLayout()
        root.addLayout(self._cards)

        charts_row = QHBoxLayout()
        self._chart_orders = MatplotlibPanel(figsize=(6.5, 3.8))
        self._chart_load = MatplotlibPanel(figsize=(6.5, 3.8))
        charts_row.addWidget(self._chart_orders)
        charts_row.addWidget(self._chart_load)
        root.addLayout(charts_row)

        self._sla_label = QLabel()
        self._sla_label.setWordWrap(True)
        root.addWidget(self._sla_label)

        self._kpi_labels: dict[str, QLabel] = {}
        self._setup_cards()

    def _setup_cards(self) -> None:
        captions = [
            ("sla_met", "% SLA соблюдения"),
            ("avg_hours", "Среднее время заявки, ч"),
            ("forecast", "Прогноз заявок / день"),
            ("success", "% успешных ремонтов"),
        ]
        for key, cap in captions:
            box = QVBoxLayout()
            val = QLabel("—")
            val.setStyleSheet("font-size:26px;font-weight:700;color:#111827;")
            cap_lbl = QLabel(cap)
            cap_lbl.setStyleSheet("color:#6b7280;font-size:12px;")
            box.addWidget(val)
            box.addWidget(cap_lbl)
            wrap = QWidget()
            wrap.setLayout(box)
            self._cards.addWidget(wrap)
            self._kpi_labels[key] = val

    def refresh(self) -> None:
        try:
            with session_scope() as session:
                analytics = AnalyticsService(session)
                summary = analytics.executive_summary()
                sla = summary["sla"]
                rep = summary["repairs"]

                self._kpi_labels["sla_met"].setText(f"{sla.get('sla_met_pct', 0):.1f}%")
                self._kpi_labels["avg_hours"].setText(f"{sla.get('avg_resolution_hours', 0):.1f}")
                self._kpi_labels["forecast"].setText(f"{summary['forecast_next_day_orders']:.2f}")
                self._kpi_labels["success"].setText(f"{rep.get('success_pct', 0):.1f}%")

                detail_lines = [
                    f"Оценено заявок: {sla.get('orders_evaluated', 0):.0f}",
                    f"Доля просрочек: {sla.get('sla_breach_pct', 0):.2f}%",
                    f"Средняя стоимость ремонта: {rep.get('avg_cost', 0):.2f}",
                    f"Средняя длительность ремонта (ч): {rep.get('avg_duration_hours', 0):.2f}",
                ]
                self._sla_label.setText(" • ".join(detail_lines))

                orders_df = analytics.orders_per_day_frame()
                load_df = analytics.engineer_workload_frame()

                fig1 = self._chart_orders.figure
                fig1.clear()
                ax1 = fig1.add_subplot(111)
                if orders_df.empty:
                    ax1.text(0.5, 0.5, "Нет данных по заявкам", ha="center")
                    ax1.axis("off")
                else:
                    tail = orders_df.tail(21)
                    ax1.bar(tail["day"].astype(str), tail["count"], color="#2563eb")
                    ax1.set_title("Заявки по дням (последние периоды)")
                    ax1.tick_params(axis="x", rotation=45)

                fig2 = self._chart_load.figure
                fig2.clear()
                ax2 = fig2.add_subplot(111)
                if load_df.empty:
                    ax2.text(0.5, 0.5, "Нет данных по загрузке", ha="center")
                    ax2.axis("off")
                else:
                    head = load_df.head(12)
                    ax2.barh(head["engineer"], head["orders"], color="#7c3aed")
                    ax2.invert_yaxis()
                    ax2.set_title("Топ инженеров по количеству заявок")

                fig1.tight_layout()
                fig2.tight_layout()
                self._chart_orders.redraw()
                self._chart_load.redraw()
        except Exception as exc:
            self._sla_label.setText(f"Ошибка загрузки данных: {exc}")
