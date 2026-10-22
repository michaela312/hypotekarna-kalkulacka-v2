"""Testy B10, B11 – kľúč extra v POST /api/calculate (krok 6 docs/v2/05-plan.md).

Každý JSON príklad z api-contract.md a z časti 2.2 02a-tiers.md má 1 test. API-R2, API-R3, API-R5, API-R6, FR-06 až FR-09.
"""
import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def body(month='', extra='', mode='shorter_term', **base):
    return {'amount': '100 000', 'rate': '4', 'years': '30', **base,
            'extra': {'month': month, 'amount': extra, 'mode': mode}}


def post(json):
    return client.post('/api/calculate', json=json)


def test_api_extra_null_ked_prazdne():
    """02a 2.2 A, FR-09: IN-04 aj IN-05 prázdne → extra: null."""
    response = post(body())
    assert response.status_code == 200
    assert response.json() == {'status': 'ok', 'results': {
        'monthly': '477,42 €', 'total': '171 869,51 €', 'interest': '71 869,51 €', 'extra': None}}


def test_api_priklad_ok_kratsia_doba():
    """api-contract.md, POST /api/calculate (= 02a 2.2 B), FR-06, API-R2: presný JSON."""
    response = post(body('12', '10 000'))
    assert response.status_code == 200
    assert response.json() == {'status': 'ok', 'results': {
        'monthly': '477,42 €', 'total': '171 869,51 €', 'interest': '71 869,51 €',
        'extra': {'mode': 'shorter_term', 'payments': '300 mesiacov (o 60 mesiacov menej)', 'lastPayment': '325,32 €',
                  'total': '153 072,49 €', 'interest': '53 072,49 €', 'interestSaved': '18 797,02 €'}}}


def test_api_priklad_ok_nizsia_splatka():
    """02a 2.2 C, FR-07: presný JSON."""
    response = post(body('12', '10 000', 'lower_payment'))
    assert response.json() == {'status': 'ok', 'results': {
        'monthly': '477,42 €', 'total': '171 869,51 €', 'interest': '71 869,51 €',
        'extra': {'mode': 'lower_payment', 'newMonthly': '428,82 €',
                  'total': '164 957,63 €', 'interest': '64 957,63 €', 'interestSaved': '6 911,88 €'}}}


def test_api_priklad_invalid_kontrakt():
    """api-contract.md, odpoveď 200 pri neplatnom vstupe: amount aj extraAmount (camelCase, API-R2, API-R5)."""
    response = post(body('12', '50', amount='999'))
    assert response.status_code == 200
    assert response.json() == {'status': 'invalid', 'errors': {
        'amount': 'Výška úveru musí byť od 1 000 do 1 000 000 €.',
        'extraAmount': 'Mimoriadna splátka musí byť od 100 do 1 000 000 €.'}}


def test_api_invalid_extra_amount():
    """02a 2.2 D, FR-09: E = zostatok → správa so zostatkom."""
    response = post(body('12', '98238,96'))
    assert response.status_code == 200
    assert response.json() == {'status': 'invalid', 'errors': {
        'extraAmount': 'Mimoriadna splátka musí byť od 100 € a menej ako zostatok úveru 98 238,96 €.'}}


def test_api_invalid_iba_jedno_pole():
    """02a 2.2 E, FR-09: vyplnený iba mesiac → chyba iba pri extraAmount."""
    assert post(body('12', '')).json() == {'status': 'invalid', 'errors': {
        'extraAmount': 'Mimoriadna splátka musí byť od 100 € a menej ako zostatok úveru 98 238,96 €.'}}


def test_api_invalid_extra_month_camel_case():
    """API-R2: kľúč chyby IN-04 je extraMonth."""
    assert post(body('360', '10 000')).json()['errors'] == {
        'extraMonth': 'Mesiac mimoriadnej splátky musí byť od 1 do 359.'}


def test_api_422_bez_extra():
    """02a 2.2 F, API-R6: chýbajúci kľúč extra je porušenie kontraktu."""
    response = post({'amount': '100 000', 'rate': '4', 'years': '30'})
    assert response.status_code == 422
    assert 'detail' in response.json()


@pytest.mark.parametrize('mode', ['faster', '', None, 'Kratšia doba'])
def test_api_422_neznamy_mode(mode):
    """02a 2.2 F, API-R6: mode musí byť shorter_term alebo lower_payment."""
    assert post(body('12', '10 000', mode)).status_code == 422


def test_api_422_extra_navyse_kluc():
    """API-R6: neznámy kľúč v extra → 422 (extra='forbid')."""
    json = body('12', '10 000')
    json['extra']['interestSaved'] = '1'
    assert post(json).status_code == 422


def test_api_422_extra_cislo_namiesto_textu():
    """API-R3: mesiac a suma sú surové texty, nie čísla."""
    json = body()
    json['extra']['month'] = 12
    assert post(json).status_code == 422


@pytest.mark.parametrize('json', [body(), body('12', '10 000'), body('12', '10 000', 'lower_payment')])
def test_api_ok_nema_errors(json):
    """Invariant api-contract.md: status 'ok' nikdy neobsahuje errors."""
    data = post(json).json()
    assert data['status'] == 'ok' and 'errors' not in data


@pytest.mark.parametrize('json', [body('12', '98238,96'), body('', '10 000'), body(amount='abc')])
def test_api_invalid_nema_results(json):
    """Invariant api-contract.md: status 'invalid' nikdy neobsahuje results."""
    data = post(json).json()
    assert data['status'] == 'invalid' and 'results' not in data
