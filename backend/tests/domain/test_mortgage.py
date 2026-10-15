"""Testy B4 calculate_mortgage – FR-01 až FR-03, DR-01 až DR-04. Scenáre z docs/v1/03-test-scenarios.md (M4)."""
import math
from decimal import Decimal

import pytest

from app.domain.mortgage import LoanParams, calculate_mortgage
from app.domain.rounding import round_half_up


def rounded(result, decimals=2):
    return tuple(round_half_up(v, decimals) for v in (result.monthly_payment, result.total_paid, result.total_interest))


@pytest.mark.parametrize('principal, rate, years, expected', [
    pytest.param(100_000, 4, 30, ('477.42', '171869.51', '71869.51'), id='test_splatka_zakladny_priklad DR-04 r1'),
    pytest.param(12_000, 0, 1, ('1000.00', '12000.00', '0.00'), id='test_splatka_nulova_sadzba DR-04 r2'),
    pytest.param(1_000_000, 20, 30, ('16710.19', '6015667.27', '5015667.27'), id='test_splatka_maximalne_hodnoty DR-04 r3'),
    pytest.param(1000, 0.01, 1, ('83.34', '1000.05', '0.05'), id='test_splatka_minimalna_kladna_sadzba DR-04 r4'),
    pytest.param(1000, 0, 1, ('83.33', '1000.00', '0.00'), id='test_splatka_minimalne_hodnoty DR-02'),
])
def test_splatka_referencne_priklady(principal, rate, years, expected):
    """FR-01, FR-02, FR-03, DR-01, DR-02, DR-04"""
    result = calculate_mortgage(LoanParams(principal, rate, years))
    assert rounded(result) == tuple(map(Decimal, expected))


def test_splatka_nulova_sadzba():
    """DR-02: P / n presne, bez zvyšku."""
    result = calculate_mortgage(LoanParams(12_000, 0, 1))
    assert (result.monthly_payment, result.total_paid, result.total_interest) == (1000, 12000, 0)


def test_splatka_vzorec_dr01():
    """DR-01: M = 477,4153… pre 100 000 €, 4 %, 30 rokov."""
    result = calculate_mortgage(LoanParams(100_000, 4, 30))
    assert math.isclose(result.monthly_payment, 477.4152954654538, rel_tol=1e-12)


def test_splatka_bez_zaokruhlenia_medzivysledkov():
    """DR-03: celková suma = M × n s nezaokrúhleným M (171 869,51 €, nie 477,42 × 360 = 171 871,20 €)."""
    result = calculate_mortgage(LoanParams(100_000, 4, 30))
    assert result.total_paid == result.monthly_payment * 360
    assert round_half_up(result.total_paid) == Decimal('171869.51')


def test_splatka_minimalna_kladna_sadzba_na_4_miesta():
    """DR-03 (príklad): M = 83,3378…, úrok 0,0542…"""
    result = calculate_mortgage(LoanParams(1000, 0.01, 1))
    assert round_half_up(result.monthly_payment, 4) == Decimal('83.3378')
    assert round_half_up(result.total_interest, 4) == Decimal('0.0542')


def test_splatka_nulova_sadzba_zvysok_float():
    """DR-02, DR-03: B4 zvyšok binárnej aritmetiky neupravuje, rieši ho až B5 (TQ-04)."""
    result = calculate_mortgage(LoanParams(1000, 0, 29))
    assert result.total_interest != 0
    assert abs(result.total_interest) < 1e-9
    assert round_half_up(result.total_interest) == Decimal('0.00')


@pytest.mark.parametrize('params', [
    pytest.param(LoanParams(1000, 0, 0), id='test_splatka_neplatna_doba_nula'),
    pytest.param(LoanParams(math.nan, 4, 30), id='test_splatka_neplatna_vyska_nan'),
    pytest.param(LoanParams(1000, -1, 30), id='test_splatka_neplatna_zaporna_sadzba'),
])
def test_splatka_neplatne_parametre(params):
    """DR-02 (TQ-01): vstup mimo kontraktu vyhodí výnimku namiesto Infinity alebo NaN."""
    with pytest.raises(ValueError, match='Neplatné parametre úveru.'):
        calculate_mortgage(params)
