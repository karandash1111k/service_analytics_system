"""Repair work performed under a service order."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base
from models.associations import repair_parts_association

if TYPE_CHECKING:
    from models.service_order import ServiceOrder
    from models.spare_part import SparePart


class Repair(Base):
    __tablename__ = "repairs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(
        ForeignKey("service_orders.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    device_type: Mapped[str] = mapped_column(String(128), nullable=False)
    device_model: Mapped[str] = mapped_column(String(255), nullable=False)
    problem_description: Mapped[str] = mapped_column(Text, nullable=False)
    repair_result: Mapped[Optional[str]] = mapped_column(Text)
    repair_status: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    repair_cost: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=0)

    service_order: Mapped["ServiceOrder"] = relationship(back_populates="repairs")
    spare_parts: Mapped[List["SparePart"]] = relationship(
        secondary=repair_parts_association,
        back_populates="repairs",
    )
