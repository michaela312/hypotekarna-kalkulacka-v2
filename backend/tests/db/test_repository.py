"""Testy B12 InMemoryRepository – FR-10, AD-V2-09."""
from datetime import UTC, datetime
from decimal import Decimal

import pytest

from app.db.repository import InMemoryRepository, StorageError
from app.services.calculator import SavedValues

VALUES = SavedValues(Decimal('100000.00'), Decimal('4.00'), 30, Decimal('477.42'), Decimal('171869.51'), Decimal('71869.51'))


def test_pamat_ulozi_zaznam():
    """FR-10: 1 uloženie = 1 záznam s id a časom v UTC."""
    repo = InMemoryRepository()
    record = repo.save(VALUES)
    assert repo.records == [record]
    assert record.values == VALUES
    assert len(record.id) == 36
    assert record.created_at.tzinfo is UTC
    assert abs((datetime.now(UTC) - record.created_at).total_seconds()) < 5


def test_pamat_rozne_id():
    repo = InMemoryRepository()
    assert repo.save(VALUES).id != repo.save(VALUES).id


def test_pamat_simulovana_chyba():
    """AD-V2-09: testy vedia simulovať nedostupnú databázu."""
    repo = InMemoryRepository(fail=True)
    with pytest.raises(StorageError):
        repo.save(VALUES)
    assert repo.records == []
