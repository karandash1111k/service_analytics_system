"""ORM models package — import side-effect registers metadata."""

from models.base import Base
from models.client import Client
from models.engineer import Engineer
from models.integration_log import IntegrationLog
from models.kpi_metric import KPIMetric
from models.repair import Repair
from models.service_order import ServiceOrder
from models.spare_part import SparePart
from models.sync_history import SyncHistory
from models.associations import repair_parts_association

__all__ = [
    "Base",
    "Client",
    "Engineer",
    "IntegrationLog",
    "KPIMetric",
    "Repair",
    "ServiceOrder",
    "SparePart",
    "SyncHistory",
    "repair_parts_association",
]
