"""B12 – rozhranie úložiska výpočtov a pamäťová implementácia.

Implementuje FR-10 (uloženie) a FR-11 (zoznam) bez závislosti na Supabase (AD-V2-09). InMemoryRepository slúži testom
a spusteniu bez databázy (STORAGE=memory).
"""
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Protocol
from uuid import uuid4

from app.services.calculator import SavedValues


class StorageError(Exception):
    """Úložisko neodpovedá alebo vrátilo chybu."""


@dataclass(frozen=True)
class SavedRecord:
    id: str
    created_at: datetime    # UTC
    values: SavedValues


LIST_LIMIT = 20   # FR-11


class CalculationRepository(Protocol):
    def save(self, values: SavedValues) -> SavedRecord:
        """Uloží 1 výpočet. Pri chybe vyhodí StorageError."""
        ...

    def list_latest(self, limit: int = LIST_LIMIT) -> list[SavedRecord]:
        """Najviac `limit` posledných záznamov, od najnovšieho. Pri chybe vyhodí StorageError."""
        ...


class InMemoryRepository:
    def __init__(self, fail: bool = False):
        self.records: list[SavedRecord] = []
        self._fail = fail   # testy: simulácia nedostupnej databázy

    def _check(self) -> None:
        if self._fail:
            raise StorageError('Pamäťové úložisko je nastavené na chybu.')

    def save(self, values: SavedValues) -> SavedRecord:
        self._check()
        record = SavedRecord(id=str(uuid4()), created_at=datetime.now(UTC), values=values)
        self.records.append(record)
        return record

    def list_latest(self, limit: int = LIST_LIMIT) -> list[SavedRecord]:
        # Poradie vloženia, nie created_at: dva záznamy v tej istej mikrosekunde majú rovnaký čas.
        self._check()
        return self.records[::-1][:limit]
