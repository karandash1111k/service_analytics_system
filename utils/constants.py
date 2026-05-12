"""Domain constants used across services and analytics."""

# Target resolution hours from creation for SLA by priority (business rule).
SLA_HOURS_BY_PRIORITY: dict[str, float] = {
    "low": 96.0,
    "medium": 48.0,
    "high": 24.0,
    "critical": 8.0,
}

DEFAULT_SLA_HOURS: float = 48.0

# Normalised external status tokens used after ETL transforms.
ORDER_STATUS_NORMALISED = (
    "new",
    "assigned",
    "in_progress",
    "completed",
    "cancelled",
)

REPAIR_STATUS_NORMALISED = (
    "pending",
    "in_progress",
    "successful",
    "failed",
    "cancelled",
)
