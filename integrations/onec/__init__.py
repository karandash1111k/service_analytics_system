"""1С integration package."""

from __future__ import annotations

__all__ = ["OneCSyncService"]


def __getattr__(name: str):
    if name == "OneCSyncService":
        from integrations.onec.onec_sync import OneCSyncService

        return OneCSyncService
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
