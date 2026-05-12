"""Inventory spare parts."""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING, List

from sqlalchemy import Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base
from models.associations import repair_parts_association

if TYPE_CHECKING:
    from models.repair import Repair


class SparePart(Base):
    __tablename__ = "spare_parts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    part_number: Mapped[str] = mapped_column(String(128), nullable=False, unique=True)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)

    repairs: Mapped[List["Repair"]] = relationship(
        secondary=repair_parts_association,
        back_populates="spare_parts",
    )
