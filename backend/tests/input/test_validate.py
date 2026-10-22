"""Testy B2 a B3 – IN-01 až IN-03, FR-05. Scenáre z docs/v1/03-test-scenarios.md (M2, M3)."""
from decimal import Decimal

import pytest

from app.input.limits import LIMITS, FieldLimits
from app.input.validate import RawInput, validate_inputs

VALID = {'amount': '100 000', 'rate': '4', 'years': '30'}


def test_limits_podla_tabulky_vstupov():
    """IN-01 až IN-05 (statické hranice)"""
    assert LIMITS == {
        'amount': FieldLimits(min=1000, max=1_000_000, decimals=2),
        'rate': FieldLimits(min=0, max=20, decimals=2),
        'years': FieldLimits(min=1, max=30, decimals=0),
        'extra_month': FieldLimits(min=1, max=359, decimals=0),
        'extra_amount': FieldLimits(min=100, max=1_000_000, decimals=2),
    }


@pytest.mark.parametrize('raw, values', [
    pytest.param(VALID, ('100000', '4', '30'), id='test_validacia_referencne_vstupy IN-01..03'),
    pytest.param({'amount': '99999,99', 'rate': '4.25', 'years': '25'}, ('99999.99', '4.25', '25'),
                 id='test_validacia_platne_priklady_z_tabulky IN-01..03'),
    pytest.param({'amount': '1000', 'rate': '0', 'years': '1'}, ('1000', '0', '1'),
                 id='test_validacia_dolne_hranice IN-01..03'),
    pytest.param({'amount': '1000000', 'rate': '20', 'years': '30'}, ('1000000', '20', '30'),
                 id='test_validacia_horne_hranice IN-01..03'),
])
def test_validacia_platne(raw, values):
    result = validate_inputs(RawInput(**raw))
    assert result.valid
    assert result.errors == {}
    assert result.values == dict(zip(('amount', 'rate', 'years'), map(Decimal, values)))


@pytest.mark.parametrize('override, errors', [
    pytest.param({'amount': '999,99'}, {'amount': 'range'}, id='test_validacia_vyska_uveru_pod_minimom IN-01'),
    pytest.param({'amount': '1000000,01'}, {'amount': 'range'}, id='test_validacia_vyska_uveru_nad_maximom IN-01'),
    pytest.param({'amount': '100,005'}, {'amount': 'step'}, id='test_validacia_vyska_uveru_privela_desatinnych IN-01'),
    pytest.param({'amount': 'abc'}, {'amount': 'nan'}, id='test_validacia_vyska_uveru_text IN-01'),
    pytest.param({'amount': ''}, {'amount': 'empty'}, id='test_validacia_vyska_uveru_prazdna IN-01'),
    pytest.param({'rate': '-0,01'}, {'rate': 'range'}, id='test_validacia_sadzba_zaporna IN-02'),
    pytest.param({'rate': '20,01'}, {'rate': 'range'}, id='test_validacia_sadzba_nad_maximom IN-02'),
    pytest.param({'rate': '3,125'}, {'rate': 'step'}, id='test_validacia_sadzba_tri_desatinne IN-02'),
    pytest.param({'rate': ''}, {'rate': 'empty'}, id='test_validacia_sadzba_prazdna IN-02'),
    pytest.param({'years': '0'}, {'years': 'range'}, id='test_validacia_doba_nula IN-03'),
    pytest.param({'years': '31'}, {'years': 'range'}, id='test_validacia_doba_nad_maximom IN-03'),
    pytest.param({'years': '2,5'}, {'years': 'step'}, id='test_validacia_doba_desatinna IN-03'),
    pytest.param({'years': ''}, {'years': 'empty'}, id='test_validacia_doba_prazdna IN-03'),
    pytest.param({'amount': '100000', 'rate': '', 'years': '2,5'}, {'rate': 'empty', 'years': 'step'},
                 id='test_validacia_dve_chyby_naraz FR-05'),
    pytest.param({'amount': 'abc', 'rate': '', 'years': '31'}, {'amount': 'nan', 'rate': 'empty', 'years': 'range'},
                 id='test_validacia_tri_chyby_naraz FR-05'),
])
def test_validacia_neplatne(override, errors):
    """FR-05: pri chybe sa nevracajú žiadne hodnoty."""
    result = validate_inputs(RawInput(**{**VALID, **override}))
    assert not result.valid
    assert result.errors == errors
    assert result.values == {}
