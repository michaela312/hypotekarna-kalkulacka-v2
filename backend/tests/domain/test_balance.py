"""Testy B4 balance_after (DR-05) a B5 round_down (IN-05) – krok 2 docs/v2/05-plan.md."""
from decimal import Decimal

import pytest

from app.domain.mortgage import LoanParams, balance_after
from app.domain.rounding import round_down, round_half_up

REF = LoanParams(100_000, 4, 30)


def test_dr05_b12():
    """DR-05: 100 000 €, 4 %, 30 rokov → B_12 = 98 238,9636…"""
    assert balance_after(REF, 12) == pytest.approx(98_238.9636, abs=1e-4)


def test_dr05_b60():
    """DR-05, DR-10 riadok 2: B_60 = 90 447,51 €."""
    assert round_half_up(balance_after(REF, 60)) == Decimal('90447.51')


def test_dr05_b6_nulova_sadzba():
    """DR-05, DR-02, DR-10 riadok 3: 12 000 €, 0 %, 1 rok → B_6 = 6 000,00 €."""
    assert round_half_up(balance_after(LoanParams(12_000, 0, 1), 6)) == Decimal('6000.00')


def test_dr05_b1_20_percent():
    """DR-05, DR-10 riadok 4: 1 000 000 €, 20 %, 30 rokov → B_1 = 999 956,48 €."""
    assert round_half_up(balance_after(LoanParams(1_000_000, 20, 30), 1)) == Decimal('999956.48')


def test_dr05_b0_je_istina():
    """DR-05: B_0 = P."""
    assert balance_after(REF, 0) == 100_000


@pytest.mark.parametrize('params', [REF, LoanParams(12_000, 0, 1)])
def test_dr05_b_n_je_nula(params):
    """DR-05: po poslednej splátke je zostatok 0 (|B_n| < 1e-6)."""
    assert abs(balance_after(params, params.years * 12)) < 1e-6


def test_dr05_b_n_velky_uver():
    """DR-05, R-P-02: pri 1 000 000 €, 20 % zostane po 360 splátkach chyba floatu ~1,4e-6 € (nad prahom 1e-6),
    ale relatívne k istine je < 1e-11. B6 preto nesmie spoliehať iba na absolútny prah."""
    params = LoanParams(1_000_000, 20, 30)
    assert abs(balance_after(params, 360)) < 1e-11 * params.principal


def test_dr05_nezaokruhluje():
    """DR-03: zostatok sa nezaokrúhľuje."""
    assert isinstance(balance_after(REF, 12), float)
    assert balance_after(REF, 12) != round(balance_after(REF, 12), 2)


@pytest.mark.parametrize('params, months', [(REF, -1), (LoanParams(0, 4, 30), 1)])
def test_dr05_neplatne_parametre(params, months):
    """TQ-01: porušenie kontraktu je ValueError."""
    with pytest.raises(ValueError):
        balance_after(params, months)


@pytest.mark.parametrize('value, expected', [
    pytest.param(98_238.9636, '98238.96', id='test_round_down_98238_9636 IN-05'),
    pytest.param(1.009, '1.00', id='test_round_down_1_009'),
    pytest.param(2.77999, '2.77', id='test_round_down_2_77999'),
    pytest.param(100.0, '100.00', id='test_round_down_cele_cislo'),
    pytest.param(Decimal('5.999'), '5.99', id='test_round_down_decimal'),
])
def test_round_down(value, expected):
    """IN-05: horná hranica mimoriadnej splátky je zostatok zaokrúhlený nadol."""
    assert round_down(value) == Decimal(expected)


@pytest.mark.parametrize('value', [-1e-9, -0.0, -0.001 + 0.001])
def test_round_down_nikdy_minus_nula(value):
    """DR-03: zvyšok binárnej aritmetiky okolo 0 dá 0,00, nikdy nie -0,00."""
    result = round_down(value)
    assert result == 0
    assert not result.is_signed()


def test_round_down_vs_half_up():
    """IN-05 vs. DR-03: 1,005 → nadol 1,00, polovica nahor 1,01."""
    assert (round_down(1.005), round_half_up(1.005)) == (Decimal('1.00'), Decimal('1.01'))
