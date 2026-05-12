"""Persistence operations for clients."""

from __future__ import annotations

from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from models.client import Client


class ClientRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_id(self, client_id: int) -> Optional[Client]:
        return self._session.get(Client, client_id)

    def list_all(self, limit: int = 10_000) -> List[Client]:
        stmt = select(Client).order_by(Client.id).limit(limit)
        return list(self._session.scalars(stmt))

    def search(self, query: str, limit: int = 500) -> List[Client]:
        q = f"%{query.strip()}%"
        stmt = (
            select(Client)
            .where(
                (Client.full_name.ilike(q))
                | (Client.email.ilike(q))
                | (Client.phone.ilike(q))
            )
            .limit(limit)
        )
        return list(self._session.scalars(stmt))

    def add(self, client: Client) -> Client:
        self._session.add(client)
        self._session.flush()
        return client
