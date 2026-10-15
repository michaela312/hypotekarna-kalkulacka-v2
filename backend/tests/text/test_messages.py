"""Testy B8 error_message – FR-05, IN-01 až IN-03. Scenáre z docs/v1/03-test-scenarios.md (M7)."""
import pytest

from app.text.messages import error_message


@pytest.mark.parametrize('field, expected', [
    pytest.param('amount', 'Výška úveru musí byť od 1 000 do 1 000 000 €.', id='test_sprava_vyska_uveru IN-01'),
    pytest.param('rate', 'Ročná úroková sadzba musí byť od 0 do 20 %.', id='test_sprava_sadzba IN-02'),
    pytest.param('years', 'Doba splácania musí byť od 1 do 30 rokov.', id='test_sprava_doba IN-03'),
])
def test_sprava(field, expected):
    """FR-05"""
    assert error_message(field, 'range') == expected


@pytest.mark.parametrize('code', ['empty', 'nan', 'step', 'range'])
def test_sprava_rovnaka_pre_vsetky_kody(code):
    """FR-05: správa uvádza iba povolený rozsah, nezávisí od kódu chyby."""
    assert error_message('amount', code) == 'Výška úveru musí byť od 1 000 do 1 000 000 €.'
