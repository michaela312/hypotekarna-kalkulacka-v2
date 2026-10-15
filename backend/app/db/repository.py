"""B12 – rozhranie úložiska výpočtov a pamäťová implementácia.

Implementuje FR-10 (uloženie) bez závislosti na Supabase (AD-V2-09). InMemoryRepository slúži testom
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


class CalculationRepository(Protocol):
    def save(self, values: SavedValues) -> SavedRecord:
        """Uloží 1 výpočet. Pri chybe vyhodí StorageError."""
        ...


class InMemoryRepository:
    def __init__(self, fail: bool = False):
        self.records: list[SavedRecord] = []
        self._fail = fail   # testy: simulácia nedostupnej databázy

    def save(self, values: SavedValues) -> SavedRecord:
        if self._fail:
            raise StorageError('Pamäťové úložisko je nastavené na chybu.')
        record = SavedRecord(id=str(uuid4()), created_at=datetime.now(UTC), values=values)
        self.records.append(record)
        return record
