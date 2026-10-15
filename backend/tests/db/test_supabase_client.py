"""Testy B13 create_supabase_client – NFR-V2-06, NFR-V2-07. Bez siete: klient sa pri vytvorení nepripája."""
import pytest

from app.config import Settings
from app.db import supabase_client
from app.db.supabase_client import TIMEOUT_SECONDS, create_supabase_client

SETTINGS = Settings(storage='supabase', supabase_url='https://abcd.supabase.co', supabase_service_role_key='kluc')


def test_klient_dostane_url_kluc_a_timeout(monkeypatch):
    """NFR-V2-06, NFR-V2-07: kľúč service_role a čakanie najviac 4 s."""
    calls = []
    monkeypatch.setattr(supabase_client, 'create_client', lambda url, key, options: calls.append((url, key, options)))
    create_supabase_client(SETTINGS)

    [(url, key, options)] = calls
    assert (url, key) == ('https://abcd.supabase.co', 'kluc')
    assert options.postgrest_client_timeout == TIMEOUT_SECONDS == 4
    assert options.persist_session is False


def test_klient_sa_da_vytvorit():
    """NFR-V2-07: skutočná knižnica supabase prijme nastavenia (bez sieťového volania)."""
    client = create_supabase_client(SETTINGS)
    assert client.table(supabase_client.TABLE) is not None


def test_klient_pri_pamatovom_ulozisku():
    """AD-V2-09: pri STORAGE=memory sa klient Supabase nevytvára."""
    with pytest.raises(ValueError):
        create_supabase_client(Settings(storage='memory'))
