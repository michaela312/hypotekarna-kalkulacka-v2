"""Testy B15 load_settings – NFR-V2-06."""
import pytest

from app.config import ConfigError, Settings, load_settings

URL = 'https://abcd.supabase.co'
KEY = 'tajny-kluc'


def test_config_supabase():
    """NFR-V2-06: URL a kľúč sa načítajú z prostredia."""
    settings = load_settings({'SUPABASE_URL': URL, 'SUPABASE_SERVICE_ROLE_KEY': KEY})
    assert settings == Settings(storage='supabase', supabase_url=URL, supabase_service_role_key=KEY)


def test_config_kluc_nie_je_v_repr():
    """NFR-V2-06: kľúč sa nevypíše v logoch."""
    settings = load_settings({'SUPABASE_URL': URL, 'SUPABASE_SERVICE_ROLE_KEY': KEY})
    assert KEY not in repr(settings)


def test_config_pamatove_uloziste_nepotrebuje_supabase():
    """AD-V2-09: STORAGE=memory funguje bez URL a kľúča."""
    assert load_settings({'STORAGE': 'memory'}) == Settings(storage='memory')


@pytest.mark.parametrize('environ, missing', [
    pytest.param({}, 'SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY', id='nic'),
    pytest.param({'SUPABASE_URL': URL}, 'SUPABASE_SERVICE_ROLE_KEY', id='bez_kluca'),
    pytest.param({'SUPABASE_SERVICE_ROLE_KEY': KEY, 'SUPABASE_URL': '  '}, 'SUPABASE_URL', id='prazdna_url'),
])
def test_config_chybajuca_premenna(environ, missing):
    """B15: pri STORAGE=supabase (predvolené) chyba uvádza názov chýbajúcej premennej."""
    with pytest.raises(ConfigError, match=f'Chýba premenná prostredia: {missing}\\.'):
        load_settings(environ)


def test_config_neplatne_storage():
    with pytest.raises(ConfigError, match="STORAGE musí byť 'supabase' alebo 'memory'"):
        load_settings({'STORAGE': 'postgres'})


def test_config_url_bez_https():
    with pytest.raises(ConfigError, match='https://'):
        load_settings({'SUPABASE_URL': 'abcd.supabase.co', 'SUPABASE_SERVICE_ROLE_KEY': KEY})
