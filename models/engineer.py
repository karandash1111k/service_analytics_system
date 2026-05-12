"""Field engineer master data."""

from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING, List

from sqlalchemy import Date, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base

if TYPE_CHECKING:
    from models.kpi_metric import KPIMetric
    from models.service_order import ServiceOrder


class Engineer(Base):
    __tablename__ = "engineers"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    specialization: Mapped[str] = mapped_column(String(128), nullable=False)
    phone: Mapped[str] = mapped_column(String(64), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    hire_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(64), nullable=False, index=True)

    service_orders: Mapped[List["ServiceOrder"]] = relationship(
        back_populates="engineer",
    )
    kpi_metrics: Mapped[List["KPIMetric"]] = relationship(
        back_populates="engineer",
        cascade="all, delete-orphan",
    )
