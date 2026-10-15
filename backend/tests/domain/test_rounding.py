"""Testy B5 round_half_up – DR-03, FR-03. Scenáre z docs/v1/03-test-scenarios.md (M5)."""
import math
from decimal import Decimal

import pytest

from app.domain.rounding import round_half_up


@pytest.mark.parametrize('value, decimals, expected', [
    pytest.param(477.4152954654538, 2, '477.42', id='test_zaokruhlenie_splatky DR-03'),
    pytest.param(0.005, 2, '0.01', id='test_zaokruhlenie_polovica_nahor DR-03'),
    pytest.param(0.004999, 2, '0.00', id='test_zaokruhlenie_tesne_pod_polovicou DR-03'),
    pytest.param(1.005, 2, '1.01', id='test_zaokruhlenie_binarna_chyba_1_005 DR-03'),
    pytest.param(2.675, 2, '2.68', id='test_zaokruhlenie_binarna_chyba_2_675 DR-03'),
    pytest.param(0.125, 2, '0.13', id='test_zaokruhlenie_nie_na_parne AD-V2-10'),
    pytest.param(2.5, 0, '3', id='test_zaokruhlenie_na_cele_cislo DR-03'),
    pytest.param(1.1368683772161603e-13, 2, '0.00', id='test_zaokruhlenie_maly_kladny_zvysok FR-03'),
    pytest.param(Decimal('999.995'), 2, '1000.00', id='test_zaokruhlenie_decimal DR-03'),
    pytest.param(1000, 0, '1000', id='test_zaokruhlenie_int DR-03'),
])
def test_zaokruhlenie(value, decimals, expected):
    assert round_half_up(value, decimals) == Decimal(expected)


def test_zaokruhlenie_maly_zaporny_zvysok():
    """DR-03, FR-03: nikdy nevráti -0."""
    result = round_half_up(-1.1368683772161603e-13, 2)
    assert result == 0
    assert not result.is_signed()


def test_zaokruhlenie_zaporna_nula_po_zaokruhleni():
    """DR-03: -0,004 sa zaokrúhli na 0,00, nie -0,00."""
    assert not round_half_up(-0.004, 2).is_signed()
    assert not round_half_up(Decimal('-0.004'), 2).is_signed()


@pytest.mark.parametrize('value', [math.nan, math.inf, Decimal('NaN')])
def test_zaokruhlenie_neplatny_vstup_nan(value):
    """DR-03 (TQ-01)"""
    with pytest.raises(ValueError, match='Neplatné číslo na zaokrúhlenie.'):
        round_half_up(value, 2)
