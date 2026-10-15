"""Testy B7 format_money, format_number – FR-04, DR-03. Scenáre z docs/v1/03-test-scenarios.md (M6)."""
import math

import pytest

from app.format.money import format_money, format_number


@pytest.mark.parametrize('value, expected', [
    pytest.param(6015667.2705, '6 015 667,27 €', id='test_format_suma_miliony FR-04'),
    pytest.param(1000, '1 000,00 €', id='test_format_suma_tisic FR-04'),
    pytest.param(0, '0,00 €', id='test_format_suma_nula FR-04'),
    pytest.param(999.99, '999,99 €', id='test_format_suma_bez_oddelovaca_tisicov FR-04'),
    pytest.param(999.995, '1 000,00 €', id='test_format_suma_zaokruhlenie_cez_tisic FR-04'),
    pytest.param(1_000_000, '1 000 000,00 €', id='test_format_suma_milion FR-04'),
    pytest.param(-1.1368683772161603e-13, '0,00 €', id='test_format_suma_bez_zapornej_nuly FR-03'),
])
def test_format_suma(value, expected):
    assert format_money(value) == expected


def test_format_suma_obycajne_medzery():
    """FR-04, AD-04: iba U+0020, žiadne nezalomiteľné medzery."""
    text = format_money(6015667.2705)
    assert ' ' not in text and ' ' not in text
    assert text.count(' ') == 3


@pytest.mark.parametrize('value, decimals, expected', [
    pytest.param(1_000_000, 0, '1 000 000', id='test_format_cislo_bez_desatinnych FR-04 (TQ-05)'),
    pytest.param(20, 0, '20', id='test_format_cislo_male FR-04'),
    pytest.param(4, 2, '4,00', id='test_format_cislo_sadzba FR-04'),
])
def test_format_cislo(value, decimals, expected):
    assert format_number(value, decimals) == expected


def test_format_suma_neplatny_vstup_nan():
    """FR-04 (TQ-01)"""
    with pytest.raises(ValueError, match='Neplatná suma na formátovanie.'):
        format_money(math.nan)
