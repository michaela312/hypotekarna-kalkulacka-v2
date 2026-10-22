"""Testy B2 a B3 pre mimoriadnu splátku – IN-04, IN-05, IN-06, FR-09 (krok 1 docs/v2/05-plan.md)."""
from decimal import Decimal

import pytest

from app.input.validate import RawInput, validate_extra_against_loan, validate_inputs

BASE = {'amount': '100 000', 'rate': '4', 'years': '30'}
FLOOR_K12 = Decimal('98238.96')   # B_12 zaokrúhlený nadol pri 100 000 €, 4 %, 30 rokov (DR-10)


def validate(month: str, extra: str = '10 000', **base):
    return validate_inputs(RawInput(**{**BASE, **base}, extra_month=month, extra_amount=extra))


@pytest.mark.parametrize('month', ['1', '359', '12'])
def test_in04_hranice_platne(month):
    """IN-04: 1 až 359 (statická hranica pri 30 rokoch)."""
    result = validate(month)
    assert result.valid
    assert result.values['extra_month'] == Decimal(month)


@pytest.mark.parametrize('month, code', [
    ('0', 'range'), ('360', 'range'), ('1,5', 'step'), ('abc', 'nan'),
])
def test_in04_hranice_neplatne(month, code):
    """IN-04, FR-09"""
    result = validate(month)
    assert not result.valid
    assert result.errors == {'extra_month': code}
    assert result.values == {}


def test_in04_pri_1_roku():
    """IN-04: pri 1 roku (n = 12) je 11 platné a 12 neplatné – hranica n − 1 závisí od úveru."""
    assert validate_extra_against_loan(11, Decimal('100'), 12, Decimal('1000')) == {}
    assert validate_extra_against_loan(12, Decimal('100'), 12, Decimal('1000')) == {'extra_month': 'range'}


@pytest.mark.parametrize('amount', ['100', '10 000', '1000000', '98238,95'])
def test_in05_hranice_platne(amount):
    """IN-05: od 100 do 1 000 000 € (statická hranica)."""
    assert validate('12', amount).valid


@pytest.mark.parametrize('amount, code', [
    ('99,99', 'range'), ('100,005', 'step'), ('abc', 'nan'), ('1000000,01', 'range'),
])
def test_in05_hranice_neplatne(amount, code):
    """IN-05, FR-09"""
    assert validate('12', amount).errors == {'extra_amount': code}


def test_in05_menej_ako_zostatok():
    """IN-05: E musí byť menej ako zostatok B_K zaokrúhlený nadol (98 238,96 € pri K = 12)."""
    assert validate_extra_against_loan(12, Decimal('98238.95'), 360, FLOOR_K12) == {}
    assert validate_extra_against_loan(12, Decimal('98238.96'), 360, FLOOR_K12) == {'extra_amount': 'range'}


def test_in05_zostatok_pod_100_nie_je_mozny():
    """FR-09: zostatok ≤ 100 € → žiadna suma nie je platná (príklad 1 000 €, 0 %, 30 rokov, K = 359)."""
    assert validate_extra_against_loan(359, None, 360, Decimal('2.77')) == {'extra_amount': 'no_room'}
    assert validate_extra_against_loan(359, Decimal('100'), 360, Decimal('100.00')) == {'extra_amount': 'no_room'}


def test_in05_staticka_chyba_sa_neporovnava_so_zostatkom():
    """FR-09: E so statickou chybou (amount=None) nemá ďalšiu chybu voči zostatku."""
    assert validate_extra_against_loan(12, None, 360, FLOOR_K12) == {}


def test_in04_neplatny_mesiac_ma_prednost_pred_zostatkom():
    """FR-09: pri K > n − 1 sa E voči zostatku neoveruje."""
    assert validate_extra_against_loan(300, Decimal('5000'), 12, Decimal('-1')) == {'extra_month': 'range'}


def test_fr09_obe_prazdne_nie_je_chyba():
    """FR-09: IN-04 aj IN-05 prázdne = bez mimoriadnej splátky, nie chyba."""
    for month, amount in [('', ''), ('  ', ' ')]:
        result = validate(month, amount)
        assert result.valid
        assert not result.has_extra
        assert set(result.values) == {'amount', 'rate', 'years'}


@pytest.mark.parametrize('month, amount, errors', [
    pytest.param('12', '', {'extra_amount': 'empty'}, id='iba_mesiac'),
    pytest.param('', '10 000', {'extra_month': 'empty'}, id='iba_suma'),
])
def test_fr09_iba_jedno_vyplnene(month, amount, errors):
    """FR-09: vyplnené iba jedno z polí → chyba pri prázdnom poli."""
    result = validate(month, amount)
    assert result.has_extra
    assert result.errors == errors


@pytest.mark.parametrize('month, code', [
    pytest.param(' ', 'empty', id='prazdne'),
    pytest.param('1,5,', 'nan', id='nie_je_cislo'),
    pytest.param('0,5', 'step', id='desatinne_pred_rozsahom'),
    pytest.param('400', 'range', id='rozsah'),
])
def test_fr09_poradie_kontrol(month, code):
    """FR-09: prázdne → nie je číslo → priveľa desatinných miest → mimo rozsahu (ako M3 vo V1)."""
    assert validate(month, '10 000').errors == {'extra_month': code}


def test_fr09_chyby_zakladu_aj_mimoriadnej_naraz():
    """FR-05, FR-09: všetky chyby naraz; partial obsahuje platné polia pre správu IN-05."""
    result = validate('12', '50', amount='999')
    assert result.errors == {'amount': 'range', 'extra_amount': 'range'}
    assert result.partial == {'rate': Decimal('4'), 'years': Decimal('30'), 'extra_month': Decimal('12')}


def test_in06_predvoleny_rezim():
    """IN-06, OQ-V2-03: predvolený režim je Kratšia doba."""
    assert RawInput(**BASE).mode == 'shorter_term'
