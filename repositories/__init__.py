"""Repository layer — data access only."""

from repositories.client_repository import ClientRepository
from repositories.engineer_repository import EngineerRepository
from repositories.integration_log_repository import IntegrationLogRepository
from repositories.order_repository import OrderRepository
from repositories.repair_repository import RepairRepository
from repositories.spare_part_repository import SparePartRepository
from repositories.kpi_repository import KPIRepository
from repositories.sync_history_repository import SyncHistoryRepository

__all__ = [
    "ClientRepository",
    "EngineerRepository",
    "IntegrationLogRepository",
    "OrderRepository",
    "RepairRepository",
    "SparePartRepository",
    "KPIRepository",
    "SyncHistoryRepository",
]
