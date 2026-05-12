"""Many-to-many association: repairs ↔ spare_parts."""

from sqlalchemy import Column, ForeignKey, Integer, Table

from models.base import Base

repair_parts_association = Table(
    "repair_parts",
    Base.metadata,
    Column(
        "repair_id",
        ForeignKey("repairs.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "spare_part_id",
        ForeignKey("spare_parts.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column("quantity_used", Integer, nullable=False, default=1),
)
