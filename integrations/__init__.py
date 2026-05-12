"""Integration adapters — external enterprise systems."""

from __future__ import annotations

__all__ = ["BitrixSyncService", "OneCSyncService"]


def __getattr__(name: str):
    if name == "BitrixSyncService":
        from integrations.bitrix24.bitrix_sync import BitrixSyncService

        return BitrixSyncService
    if name == "OneCSyncService":
        from integrations.onec.onec_sync import OneCSyncService

        return OneCSyncService
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
