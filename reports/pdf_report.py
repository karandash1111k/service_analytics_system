"""PDF bundle combining KPI narrative plots via matplotlib."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

if TYPE_CHECKING:
    from services.analytics_service import AnalyticsService


class PdfAnalyticsReport:
    """Embeds charts + summary tables into a multi-page PDF."""

    def __init__(self, analytics: "AnalyticsService") -> None:
        self._analytics = analytics

    def write(self, output_path: str | Path) -> Path:
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        summary = self._analytics.executive_summary()

        orders_day = self._analytics.orders_per_day_frame()
        workload = self._analytics.engineer_workload_frame()
        outcomes = self._analytics.repairs_outcome_frame()

        with PdfPages(path) as pdf:
            fig, ax = plt.subplots(figsize=(11.69, 8.27))
            ax.axis("off")
            lines = [
                "Корпоративная аналитика выездного сервиса",
                f"Сформировано: {summary['generated_at']}",
                "",
                "SLA:",
                *[f"  {k}: {v}" for k, v in summary["sla"].items()],
                "",
                "Ремонты:",
                *[f"  {k}: {v}" for k, v in summary["repairs"].items()],
                "",
                f"Прогноз заявок на след. день (скользящее среднее): {summary['forecast_next_day_orders']}",
            ]
            ax.text(0.02, 0.98, "\n".join(lines), va="top", fontsize=11, family="sans-serif")
            pdf.savefig(fig)
            plt.close(fig)

            if not orders_day.empty:
                fig, ax = plt.subplots(figsize=(11.69, 8.27))
                ax.bar(orders_day["day"].astype(str), orders_day["count"], color="#2E86AB")
                ax.set_title("Заявки по дням")
                ax.set_xlabel("Дата")
                ax.set_ylabel("Количество")
                plt.xticks(rotation=45, ha="right")
                fig.tight_layout()
                pdf.savefig(fig)
                plt.close(fig)

            if not workload.empty:
                fig, ax = plt.subplots(figsize=(11.69, 8.27))
                top = workload.head(15)
                ax.barh(top["engineer"], top["orders"], color="#A23B72")
                ax.invert_yaxis()
                ax.set_title("Нагрузка инженеров (кол-во заявок)")
                fig.tight_layout()
                pdf.savefig(fig)
                plt.close(fig)

            if not outcomes.empty:
                fig, ax = plt.subplots(figsize=(11.69, 8.27))
                ax.pie(outcomes["count"], labels=outcomes["status"], autopct="%1.1f%%")
                ax.set_title("Исходы ремонтов")
                pdf.savefig(fig)
                plt.close(fig)

        return path
