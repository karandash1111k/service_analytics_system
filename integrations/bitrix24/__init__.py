"""Bitrix24 integration package."""

from __future__ import annotations

__all__ = ["BitrixSyncService"]


def __getattr__(name: str):
    if name == "BitrixSyncService":
        from integrations.bitrix24.bitrix_sync import BitrixSyncService

        return BitrixSyncService
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
