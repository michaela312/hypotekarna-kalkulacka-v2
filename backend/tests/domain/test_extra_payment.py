"""Testy B6 calculate_extra – FR-06, FR-07, FR-08, DR-05 až DR-10 (krok 3 docs/v2/05-plan.md)."""
from decimal import Decimal

import pytest

from app.domain.extra_payment import ExtraParams, ExtraResultRaw, calculate_extra
from app.domain.mortgage import LoanParams
from app.domain.rounding import round_half_up

# DR-10, režim „Kratšia doba“: P, sadzba, roky, K, E → splátok, posledná, celkom, úrok, ušetrený úrok
SHORTER = [
    pytest.param((100_000, 4, 30, 12, 10_000), (300, '325.32', '153072.49', '53072.49', '18797.02'), id='r1'),
    pytest.param((100_000, 4, 30, 60, 50_000), (160, '344.53', '126253.56', '26253.56', '45615.95'), id='r2'),
    pytest.param((12_000, 0, 1, 6, 1_200), (11, '800.00', '12000.00', '0.00', '0.00'), id='r3_nulova_sadzba'),
    pytest.param((1_000_000, 20, 30, 1, 100), (358, '12774.40', '5978411.11', '4978411.11', '37256.16'), id='r4'),
]

# DR-10, režim „Nižšia splátka“: → nová splátka, celkom, úrok, ušetrený úrok
LOWER = [
    pytest.param((100_000, 4, 30, 12, 10_000), ('428.82', '164957.63', '64957.63', '6911.88'), id='r1'),
    pytest.param((100_000, 4, 30, 60, 50_000), ('213.50', '142693.98', '42693.98', '29175.53'), id='r2'),
    pytest.param((12_000, 0, 1, 6, 1_200), ('800.00', '12000.00', '0.00', '0.00'), id='r3_nulova_sadzba'),
    pytest.param((1_000_000, 20, 30, 1, 100), ('16708.52', '6015167.35', '5015167.35', '499.92'), id='r4'),
]


def run(row, mode) -> ExtraResultRaw:
    p, rate, years, k, e = row
    return calculate_extra(LoanParams(p, rate, years), ExtraParams(month=k, amount=e, mode=mode))


def r(value) -> str:
    return str(round_half_up(value))


@pytest.mark.parametrize('row, expected', SHORTER)
def test_dr10_kratsia_doba(row, expected):
    """FR-06, FR-08, DR-07, DR-09: každý riadok DR-10 presne na 0,01 €."""
    result = run(row, 'shorter_term')
    payments, last, total, interest, saved = expected
    assert result.payments == payments
    assert (r(result.last_payment), r(result.total_paid), r(result.total_interest), r(result.interest_saved)) == \
        (last, total, interest, saved)
    assert result.new_monthly is None


@pytest.mark.parametrize('row, expected', LOWER)
def test_dr10_nizsia_splatka(row, expected):
    """FR-07, FR-08, DR-08, DR-09: každý riadok DR-10 presne na 0,01 €."""
    result = run(row, 'lower_payment')
    assert (r(result.new_monthly), r(result.total_paid), r(result.total_interest), r(result.interest_saved)) == expected
    assert result.payments is None and result.last_payment is None


def test_dr06_dr07_priklad_fr06_nezaokruhleny():
    """DR-06, DR-07: B'_12 = B_12 − E; posledná splátka 325,3178… a m = 288 po mesiaci 12."""
    result = run((100_000, 4, 30, 12, 10_000), 'shorter_term')
    assert result.last_payment == pytest.approx(325.3178, abs=1e-4)
    assert result.payments - 12 == 288


def test_dr08_priklad_fr07_nezaokruhleny():
    """DR-08: M' = 428,8179…"""
    assert run((100_000, 4, 30, 12, 10_000), 'lower_payment').new_monthly == pytest.approx(428.8179, abs=1e-4)


@pytest.mark.parametrize('mode', ['shorter_term', 'lower_payment'])
def test_fr08_nulova_sadzba_usetri_0(mode):
    """FR-08: pri sadzbe 0 % je ušetrený úrok vždy 0,00 € (bez -0,00)."""
    for k, e in [(1, 100), (6, 1_200), (11, 999)]:
        saved = round_half_up(run((12_000, 0, 1, k, e), mode).interest_saved)
        assert saved == 0 and not saved.is_signed()


def test_dr07_cyklus_konci_najviac_po_n_splatkach():
    """DR-07, R-P-02: K = 1, E = 100 pri 1 000 000 €, 20 % – počet splátok ≤ n a posledná splátka ≤ M."""
    result = run((1_000_000, 20, 30, 1, 100), 'shorter_term')
    assert result.payments <= 360
    assert 0 < result.last_payment <= 16_710.19


@pytest.mark.parametrize('k', [1, 180, 359])
def test_dr07_najmensia_mimoriadna_splatka_nepredlzi_uver(k):
    """DR-07: E = 100 € nikdy nepredĺži úver nad n splátok ani nevytvorí splátku navyše (R-P-02)."""
    result = run((1_000_000, 20, 30, k, 100), 'shorter_term')
    assert k < result.payments <= 360
    assert result.last_payment > 0


@pytest.mark.parametrize('mode', ['shorter_term', 'lower_payment'])
def test_dr09_celkovy_urok_je_celkom_minus_istina(mode):
    """DR-09: celkový úrok = celkom − P."""
    result = run((100_000, 4, 30, 60, 50_000), mode)
    assert result.total_interest == pytest.approx(result.total_paid - 100_000)


def test_b6_nezaokruhluje():
    """DR-03: výsledok B6 sú nezaokrúhlené floaty, nie Decimal."""
    result = run((100_000, 4, 30, 12, 10_000), 'shorter_term')
    for value in (result.total_paid, result.total_interest, result.interest_saved, result.last_payment):
        assert isinstance(value, float) and not isinstance(value, Decimal)
    assert result.total_paid != round(result.total_paid, 2)


@pytest.mark.parametrize('k, e', [(0, 100), (360, 100), (12, 0), (12, 98_239)])
def test_b6_porusenie_kontraktu(k, e):
    """TQ-01: K mimo 1..n−1, E ≤ 0 alebo E ≥ B_K je ValueError (B9 to nikdy neodovzdá)."""
    with pytest.raises(ValueError):
        run((100_000, 4, 30, k, e), 'shorter_term')
