"""Testy B7 format_rate a B8 textov V2 – FR-06, FR-09, FR-11 (krok 4 docs/v2/05-plan.md)."""
from decimal import Decimal

import pytest

from app.format.money import format_rate
from app.text.messages import (
    extra_amount_message, extra_month_message, extra_text, payments_text, plural, years_text,
)


@pytest.mark.parametrize('count, mesiac, rok', [
    (0, 'mesiacov', 'rokov'), (1, 'mesiac', 'rok'), (2, 'mesiace', 'roky'), (4, 'mesiace', 'roky'),
    (5, 'mesiacov', 'rokov'), (11, 'mesiacov', 'rokov'), (60, 'mesiacov', 'rokov'), (300, 'mesiacov', 'rokov'),
])
def test_plural(count, mesiac, rok):
    """FR-06, FR-11: 1 → mesiac/rok, 2 až 4 → mesiace/roky, 0 a 5+ → mesiacov/rokov."""
    assert (plural(count, 'mesiac'), plural(count, 'rok')) == (mesiac, rok)


@pytest.mark.parametrize('max_month, expected', [
    (359, 'Mesiac mimoriadnej splátky musí byť od 1 do 359.'),
    (11, 'Mesiac mimoriadnej splátky musí byť od 1 do 11.'),
])
def test_fr09_sprava_in04(max_month, expected):
    """FR-09: horná hranica IN-04 je n − 1."""
    assert extra_month_message(max_month) == expected


def test_fr09_sprava_in05_so_zostatkom():
    """FR-09, riadok 2: IN-01 až IN-04 platné → správa so zostatkom."""
    assert extra_amount_message('range', 12, Decimal('98238.96')) == \
        'Mimoriadna splátka musí byť od 100 € a menej ako zostatok úveru 98 238,96 €.'


@pytest.mark.parametrize('code', ['empty', 'nan', 'step', 'range'])
def test_fr09_sprava_in05_bez_zostatku(code):
    """FR-09, riadok 3: niektorý z IN-01 až IN-04 je neplatný → statický rozsah."""
    assert extra_amount_message(code) == 'Mimoriadna splátka musí byť od 100 do 1 000 000 €.'


def test_fr09_sprava_zostatok_pod_100():
    """FR-09, riadok 4: príklad 1 000 €, 0 %, 30 rokov, K = 359."""
    assert extra_amount_message('no_room', 359, Decimal('2.77')) == \
        'V mesiaci 359 je zostatok úveru 2,77 €, mimoriadna splátka (min. 100 €) nie je možná.'


@pytest.mark.parametrize('payments, n, expected', [
    (300, 360, '300 mesiacov (o 60 mesiacov menej)'),
    (160, 360, '160 mesiacov (o 200 mesiacov menej)'),
    (11, 12, '11 mesiacov (o 1 mesiac menej)'),
    (358, 360, '358 mesiacov (o 2 mesiace menej)'),
    (2, 3, '2 mesiace (o 1 mesiac menej)'),
])
def test_fr06_text_splatok(payments, n, expected):
    """FR-06, DR-10"""
    assert payments_text(payments, n) == expected


@pytest.mark.parametrize('years, expected', [(1, '1 rok'), (3, '3 roky'), (30, '30 rokov')])
def test_fr11_text_doby(years, expected):
    """FR-11"""
    assert years_text(years) == expected


@pytest.mark.parametrize('mode, expected', [
    ('shorter_term', '10 000,00 € v 12. mesiaci, kratšia doba'),
    ('lower_payment', '10 000,00 € v 12. mesiaci, nižšia splátka'),
])
def test_fr11_text_extra(mode, expected):
    """FR-11: oba režimy."""
    assert extra_text(Decimal('10000.00'), 12, mode) == expected


@pytest.mark.parametrize('value, expected', [
    (4, '4,00 %'), (0, '0,00 %'), (20, '20,00 %'), (3.5, '3,50 %'), (Decimal('0.01'), '0,01 %'),
])
def test_fr11_format_rate(value, expected):
    """FR-11: sadzba v tvare 4,00 %."""
    assert format_rate(value) == expected
