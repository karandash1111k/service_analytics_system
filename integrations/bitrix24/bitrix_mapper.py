"""Maps Bitrix24 payloads into transformer-friendly dictionaries."""

from __future__ import annotations

from typing import Any, Dict, List


def deals_to_internal(deals: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Pass-through with shallow copy — ETL transformer owns semantics."""
    return [dict(d) for d in deals]
