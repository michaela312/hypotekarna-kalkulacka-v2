"""Testy B1 parse_number – IN-01 až IN-03, FR-05. Scenáre z docs/v1/03-test-scenarios.md (M1)."""
from decimal import Decimal

import pytest

from app.input.parse import ParsedNumber, parse_number


@pytest.mark.parametrize('raw, value, decimals', [
    pytest.param('1000', '1000', 0, id='test_parse_cele_cislo IN-01'),
    pytest.param('150 000', '150000', 0, id='test_parse_medzery_medzi_cislicami IN-01'),
    pytest.param('3,5', '3.5', 1, id='test_parse_desatinna_ciarka IN-02'),
    pytest.param('4.25', '4.25', 2, id='test_parse_desatinna_bodka IN-02'),
    pytest.param('  25  ', '25', 0, id='test_parse_orezanie_okrajovych_medzier IN-03'),
    pytest.param('100,005', '100.005', 3, id='test_parse_tri_desatinne_miesta IN-01'),
    pytest.param('-0,01', '-0.01', 2, id='test_parse_zaporne_cislo IN-02'),
    pytest.param('150 000', '150000', 0, id='test_parse_nezalomitelna_medzera IN-01'),
])
def test_parse_cislo(raw, value, decimals):
    assert parse_number(raw) == ParsedNumber(ok=True, value=Decimal(value), decimals=decimals)


@pytest.mark.parametrize('raw, reason', [
    pytest.param('', 'empty', id='test_parse_prazdny_retazec FR-05'),
    pytest.param('   ', 'empty', id='test_parse_iba_medzery FR-05'),
    pytest.param('abc', 'nan', id='test_parse_text FR-05'),
    pytest.param('1e3', 'nan', id='test_parse_exponent FR-05'),
    pytest.param('0x10', 'nan', id='test_parse_hexadecimalne FR-05'),
    pytest.param('1,2,3', 'nan', id='test_parse_viac_oddelovacov FR-05'),
    pytest.param('3,', 'nan', id='test_parse_oddelovac_bez_cislic FR-05'),
    pytest.param('١٢', 'nan', id='test_parse_iba_ascii_cislice FR-05'),
])
def test_parse_neplatne(raw, reason):
    assert parse_number(raw) == ParsedNumber(ok=False, reason=reason)
