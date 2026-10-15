"""Testy B14 – výber úložiska pri štarte podľa B15 (NFR-V2-06, AD-V2-09)."""
import pytest
from fastapi.testclient import TestClient

from app import main
from app.config import ConfigError, Settings
from app.db.repository import InMemoryRepository
from app.db.supabase_repository import SupabaseRepository


def start_with(monkeypatch, settings_or_error):
    def fake_load_settings():
        if isinstance(settings_or_error, Exception):
            raise settings_or_error
        return settings_or_error
    monkeypatch.setattr(main, 'load_settings', fake_load_settings)
    with TestClient(main.app) as client:    # 'with' spustí lifespan
        return client.app.state.repository


def test_start_pamatove_uloziste(monkeypatch):
    """AD-V2-09: STORAGE=memory → InMemoryRepository."""
    assert isinstance(start_with(monkeypatch, Settings(storage='memory')), InMemoryRepository)


def test_start_supabase(monkeypatch):
    """FR-10: STORAGE=supabase → SupabaseRepository (pri vytvorení sa nepripája)."""
    settings = Settings(storage='supabase', supabase_url='https://abcd.supabase.co', supabase_service_role_key='k')
    assert isinstance(start_with(monkeypatch, settings), SupabaseRepository)


def test_start_bez_premennych_zlyha(monkeypatch):
    """B15, NFR-V2-06: pri chýbajúcej premennej sa aplikácia nespustí a chyba uvádza jej názov."""
    with pytest.raises(ConfigError, match='SUPABASE_URL'):
        start_with(monkeypatch, ConfigError('Chýba premenná prostredia: SUPABASE_URL.'))
