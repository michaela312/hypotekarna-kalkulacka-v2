"""Akceptačné testy B9 run_calculation – FR-01 až FR-05, DR-04. Scenáre z docs/v1/03-test-scenarios.md (M8)."""
import pytest

from app.input.validate import RawInput
from app.services.calculator import CalculationResponse, Results, run_calculation

AMOUNT = 'Výška úveru musí byť od 1 000 do 1 000 000 €.'
RATE = 'Ročná úroková sadzba musí byť od 0 do 20 %.'
YEARS = 'Doba splácania musí byť od 1 do 30 rokov.'


@pytest.mark.parametrize('raw, expected', [
    pytest.param(('100000', '4', '30'), ('477,42 €', '171 869,51 €', '71 869,51 €'),
                 id='test_vypocet_referencny_priklad DR-04 r1'),
    pytest.param(('12000', '0', '1'), ('1 000,00 €', '12 000,00 €', '0,00 €'),
                 id='test_vypocet_referencny_priklad_nulova_sadzba DR-04 r2'),
    pytest.param(('1000000', '20', '30'), ('16 710,19 €', '6 015 667,27 €', '5 015 667,27 €'),
                 id='test_vypocet_referencny_priklad_maximum DR-04 r3'),
    pytest.param(('1000', '0,01', '1'), ('83,34 €', '1 000,05 €', '0,05 €'),
                 id='test_vypocet_referencny_priklad_minimalna_sadzba DR-04 r4'),
    pytest.param(('150 000', '3,5', '25'), ('750,94 €', '225 280,61 €', '75 280,61 €'),
                 id='test_vypocet_medzery_a_ciarka IN-01 IN-02'),
    pytest.param(('100000', '3,5', '30'), ('449,04 €', '161 656,09 €', '61 656,09 €'),
                 id='test_vypocet_ciarka IN-02'),
    pytest.param(('100000', '3.5', '30'), ('449,04 €', '161 656,09 €', '61 656,09 €'),
                 id='test_vypocet_bodka IN-02'),
    pytest.param(('99999,99', '4.25', '25'), ('541,74 €', '162 521,41 €', '62 521,42 €'),
                 id='test_vypocet_desatinna_vyska_uveru IN-01 FR-03'),
    pytest.param(('1000', '0', '1'), ('83,33 €', '1 000,00 €', '0,00 €'),
                 id='test_vypocet_dolne_hranice DR-02'),
    pytest.param(('1000', '0', '29'), ('2,87 €', '1 000,00 €', '0,00 €'),
                 id='test_vypocet_nulova_sadzba_bez_zapornej_nuly FR-03 DR-03'),
    pytest.param(('1000', '4', '30'), ('4,77 €', '1 718,70 €', '718,70 €'),
                 id='test_vypocet_minimalna_vyska_uveru IN-01'),
    pytest.param(('100000', '4', '25'), ('527,84 €', '158 351,05 €', '58 351,05 €'),
                 id='test_vypocet_25_rokov IN-03'),
])
def test_vypocet_platny(raw, expected):
    """FR-01, FR-02, FR-03, FR-04"""
    result = run_calculation(RawInput(*raw))
    assert result == CalculationResponse(status='ok', results=Results(*expected))
    assert result.errors == {}


@pytest.mark.parametrize('raw, errors', [
    pytest.param(('999', '4', '30'), {'amount': AMOUNT}, id='test_vypocet_neplatna_vyska_uveru FR-05'),
    pytest.param(('1000000,01', '4', '30'), {'amount': AMOUNT}, id='test_vypocet_vyska_uveru_tesne_nad_maximom FR-05'),
    pytest.param(('100000', '4', '31'), {'years': YEARS}, id='test_vypocet_neplatna_doba FR-05'),
    pytest.param(('100000', '', '2,5'), {'rate': RATE, 'years': YEARS}, id='test_vypocet_dve_chyby_naraz FR-05'),
    pytest.param(('abc', '20,01', '0'), {'amount': AMOUNT, 'rate': RATE, 'years': YEARS},
                 id='test_vypocet_tri_chyby_naraz FR-05'),
])
def test_vypocet_neplatny(raw, errors):
    """FR-05: pri chybe žiadne výsledky."""
    result = run_calculation(RawInput(*raw))
    assert result == CalculationResponse(status='invalid', errors=errors)
    assert result.results is None
