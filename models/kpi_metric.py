"""Persisted KPI snapshots per engineer."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base

if TYPE_CHECKING:
    from models.engineer import Engineer


class KPIMetric(Base):
    __tablename__ = "kpi_metrics"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    engineer_id: Mapped[int] = mapped_column(
        ForeignKey("engineers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    metric_name: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    metric_value: Mapped[Decimal] = mapped_column(Numeric(18, 6), nullable=False)
    calculated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    engineer: Mapped["Engineer"] = relationship(back_populates="kpi_metrics")
