"""Akceptačné testy B9 s mimoriadnou splátkou – FR-06 až FR-10, DR-10, NFR-V2-02 (krok 5 docs/v2/05-plan.md)."""
import statistics
import time
from decimal import Decimal

import pytest

from app.input.validate import RawInput
from app.services.calculator import (
    CalculationResponse, ExtraResult, Results, SavedExtra, SavedValues, run_calculation,
)

AMOUNT = 'Výška úveru musí byť od 1 000 do 1 000 000 €.'
YEARS = 'Doba splácania musí byť od 1 do 30 rokov.'
MONTH_359 = 'Mesiac mimoriadnej splátky musí byť od 1 do 359.'
EXTRA_STATIC = 'Mimoriadna splátka musí byť od 100 do 1 000 000 €.'
EXTRA_K12 = 'Mimoriadna splátka musí byť od 100 € a menej ako zostatok úveru 98 238,96 €.'
NO_ROOM = 'V mesiaci 359 je zostatok úveru 2,77 €, mimoriadna splátka (min. 100 €) nie je možná.'

BASE_RESULTS = {
    (100_000, 4, 30): ('477,42 €', '171 869,51 €', '71 869,51 €'),
    (12_000, 0, 1): ('1 000,00 €', '12 000,00 €', '0,00 €'),
    (1_000_000, 20, 30): ('16 710,19 €', '6 015 667,27 €', '5 015 667,27 €'),
}


def calc(amount, rate, years, month='', extra='', mode='shorter_term'):
    return run_calculation(RawInput(str(amount), str(rate), str(years), str(month), str(extra), mode))


@pytest.mark.parametrize('loan, k, e, extra', [
    pytest.param((100_000, 4, 30), 12, 10_000, ('300 mesiacov (o 60 mesiacov menej)', '325,32 €',
                 '153 072,49 €', '53 072,49 €', '18 797,02 €'), id='r1 FR-06'),
    pytest.param((100_000, 4, 30), 60, 50_000, ('160 mesiacov (o 200 mesiacov menej)', '344,53 €',
                 '126 253,56 €', '26 253,56 €', '45 615,95 €'), id='r2 FR-06'),
    pytest.param((12_000, 0, 1), 6, 1_200, ('11 mesiacov (o 1 mesiac menej)', '800,00 €',
                 '12 000,00 €', '0,00 €', '0,00 €'), id='r3 FR-06 FR-08'),
    pytest.param((1_000_000, 20, 30), 1, 100, ('358 mesiacov (o 2 mesiace menej)', '12 774,40 €',
                 '5 978 411,11 €', '4 978 411,11 €', '37 256,16 €'), id='r4 FR-06'),
])
def test_dr10_akceptacia_kratsia_doba(loan, k, e, extra):
    """DR-10, FR-06, FR-08: texty presne podľa tabuľky; základné výsledky FR-01 až FR-03 sa nemenia."""
    payments, last, total, interest, saved = extra
    response = calc(*loan, k, e).response
    assert response == CalculationResponse(status='ok', results=Results(*BASE_RESULTS[loan], extra=ExtraResult(
        mode='shorter_term', payments=payments, last_payment=last, total=total, interest=interest,
        interest_saved=saved)))


@pytest.mark.parametrize('loan, k, e, extra', [
    pytest.param((100_000, 4, 30), 12, 10_000, ('428,82 €', '164 957,63 €', '64 957,63 €', '6 911,88 €'),
                 id='r1 FR-07'),
    pytest.param((100_000, 4, 30), 60, 50_000, ('213,50 €', '142 693,98 €', '42 693,98 €', '29 175,53 €'),
                 id='r2 FR-07'),
    pytest.param((12_000, 0, 1), 6, 1_200, ('800,00 €', '12 000,00 €', '0,00 €', '0,00 €'), id='r3 FR-07 FR-08'),
    pytest.param((1_000_000, 20, 30), 1, 100, ('16 708,52 €', '6 015 167,35 €', '5 015 167,35 €', '499,92 €'),
                 id='r4 FR-07'),
])
def test_dr10_akceptacia_nizsia_splatka(loan, k, e, extra):
    """DR-10, FR-07, FR-08"""
    new_monthly, total, interest, saved = extra
    response = calc(*loan, k, e, 'lower_payment').response
    assert response.results.extra == ExtraResult(
        mode='lower_payment', new_monthly=new_monthly, total=total, interest=interest, interest_saved=saved)
    assert response.results.monthly == BASE_RESULTS[loan][0]


def test_fr09_extra_null_ked_obe_prazdne():
    """FR-09: IN-04 aj IN-05 prázdne → iba FR-01 až FR-03, extra = None."""
    outcome = calc(100_000, 4, 30)
    assert outcome.response.results.extra is None
    assert outcome.values.extra is None


@pytest.mark.parametrize('raw, errors', [
    pytest.param((100_000, 4, 30, '360', '10 000'), {'extra_month': MONTH_359}, id='r1 IN-04 neplatny'),
    pytest.param((100_000, 4, 1, '12', '500'), {'extra_month': 'Mesiac mimoriadnej splátky musí byť od 1 do 11.'},
                 id='r1 IN-04 nad n-1 pri 1 roku'),
    pytest.param((100_000, 4, 30, '12', '98238,96'), {'extra_amount': EXTRA_K12}, id='r2 IN-05 rovne zostatku'),
    pytest.param((100_000, 4, 30, '12', '99,99'), {'extra_amount': EXTRA_K12}, id='r2 IN-05 pod 100'),
    pytest.param((999, 4, 30, '12', '50'), {'amount': AMOUNT, 'extra_amount': EXTRA_STATIC}, id='r3 IN-01 aj IN-05'),
    pytest.param((100_000, 4, 30, 'abc', '50'), {'extra_month': MONTH_359, 'extra_amount': EXTRA_STATIC},
                 id='r3 IN-04 aj IN-05'),
    pytest.param((1_000, 0, 30, '359', ''), {'extra_amount': NO_ROOM}, id='r4 zostatok pod 100'),
    pytest.param((100_000, 4, 30, '12', ''), {'extra_amount': EXTRA_K12}, id='r5 iba IN-04'),
    pytest.param((100_000, 4, 30, '', '10 000'), {'extra_month': MONTH_359}, id='r5 iba IN-05'),
])
def test_fr09_tabulka(raw, errors):
    """FR-09: každý riadok tabuľky správ."""
    assert calc(*raw).response == CalculationResponse(status='invalid', errors=errors)


def test_fr09_neplatny_in03_hranica_in04_je_359():
    """FR-09: pri neplatnom IN-03 je horná hranica IN-04 359."""
    response = calc(100_000, 4, 31, '400', '10 000').response
    assert response.errors == {'years': YEARS, 'extra_month': MONTH_359}


def test_fr09_ziadne_vysledky_pri_chybe():
    """FR-09: pri chybe mimoriadnej splátky sa nezobrazia ani výsledky FR-01 až FR-03 a nič sa neuloží."""
    outcome = calc(100_000, 4, 30, '12', '98238,96')
    assert outcome.response.results is None
    assert outcome.values is None


def test_fr10_saved_extra_zaokruhlene():
    """FR-10, AD-V2-08: DR-10 riadok 1 → SavedExtra zaokrúhlené na 0,01 €."""
    values = calc('100 000', 4, 30, '12', '10 000').values
    assert values == SavedValues(
        amount=Decimal('100000.00'), rate=Decimal('4.00'), years=30, monthly_payment=Decimal('477.42'),
        total_paid=Decimal('171869.51'), total_interest=Decimal('71869.51'),
        extra=SavedExtra(month=12, amount=Decimal('10000.00'), mode='shorter_term', payments=300,
                         last_payment=Decimal('325.32'), new_monthly=None, total_paid=Decimal('153072.49'),
                         total_interest=Decimal('53072.49'), interest_saved=Decimal('18797.02')))


def test_fr10_saved_extra_nizsia_splatka():
    """FR-10: v režime lower_payment je payments a last_payment None, new_monthly vyplnené."""
    extra = calc(100_000, 4, 30, '12', '10 000', 'lower_payment').values.extra
    assert (extra.payments, extra.last_payment, extra.new_monthly) == (None, None, Decimal('428.82'))


def test_nfr_v2_02():
    """NFR-V2-02: K = 1, 30 rokov – medián zo 100 výpočtov B9 ≤ 50 ms."""
    durations = []
    for _ in range(100):
        start = time.perf_counter()
        calc(1_000_000, 20, 30, '1', '100')
        durations.append(time.perf_counter() - start)
    assert statistics.median(durations) <= 0.050
