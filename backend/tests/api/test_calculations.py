"""Testy B7a, B10, B11, B14 – POST a GET /api/calculations, 503 handler (krok 8 docs/v2/05-plan.md).

FR-10, FR-11, API-R5, API-R6, AD-V2-12, AD-V2-15. Každý riadok tabuliek kódov v api-contract.md má 1 test.
"""
from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient

from app.api.routes import get_repository
from app.db.repository import InMemoryRepository, SavedRecord
from app.format.datetime import format_datetime
from app.main import app
from app.services.calculator import SavedValues

client = TestClient(app)
DATE = r'\d{1,2}\. \d{1,2}\. \d{4} \d{2}:\d{2}'


def body(month='', extra='', mode='shorter_term', **base):
    return {'amount': '100 000', 'rate': '4', 'years': '30', **base,
            'extra': {'month': month, 'amount': extra, 'mode': mode}}


@pytest.fixture
def failing():
    app.dependency_overrides[get_repository] = lambda: InMemoryRepository(fail=True)


# --- B7a format_datetime (FR-11) ----------------------------------------------------------------

def test_b7a_leto():
    """FR-11: UTC 12:05 v júli → 14:05 (letný čas, UTC+2)."""
    assert format_datetime(datetime(2026, 7, 15, 12, 5, tzinfo=UTC)) == '15. 7. 2026 14:05'


def test_b7a_zima():
    """FR-11: UTC 13:05 v januári → 14:05 (zimný čas, UTC+1)."""
    assert format_datetime(datetime(2026, 1, 15, 13, 5, tzinfo=UTC)) == '15. 1. 2026 14:05'


def test_b7a_format_bez_nul():
    """FR-11: deň a mesiac bez úvodnej nuly, hodina a minúta s nulou."""
    assert format_datetime(datetime(2026, 1, 5, 7, 3, tzinfo=UTC)) == '5. 1. 2026 08:03'


def test_b7a_priklad_fr11():
    """FR-11: príklad 15. 10. 2026 14:05 (UTC 12:05, letný čas)."""
    assert format_datetime(datetime(2026, 10, 15, 12, 5, tzinfo=UTC)) == '15. 10. 2026 14:05'


def test_b7a_bez_casoveho_pasma():
    """TQ-01: naivný datetime je porušenie kontraktu."""
    with pytest.raises(ValueError):
        format_datetime(datetime(2026, 10, 15, 12, 5))


# --- POST /api/calculations (FR-10) -------------------------------------------------------------

def test_post_calculations_201(repository):
    """FR-10, api-contract.md 201: telo { id, createdAt }."""
    response = client.post('/api/calculations', json=body())
    assert response.status_code == 201
    data = response.json()
    assert set(data) == {'id', 'createdAt'}
    assert data['id'] == repository.records[0].id
    assert data['createdAt'] == format_datetime(repository.records[0].created_at)


def test_post_calculations_ulozi_1_zaznam(repository):
    """FR-10: príklad 100 000 €, 4 %, 30 rokov → 1 riadok s monthly_payment = 477.42."""
    client.post('/api/calculations', json=body())
    [record] = repository.records
    assert record.values.monthly_payment == Decimal('477.42')
    assert record.values.extra is None


def test_post_calculations_s_extra(repository):
    """FR-10: uloží sa aj mimoriadna splátka (DR-10 riadok 1) zaokrúhlená na 0,01 €."""
    client.post('/api/calculations', json=body('12', '10 000'))
    extra = repository.records[0].values.extra
    assert (extra.month, extra.amount, extra.mode, extra.payments, extra.interest_saved) == \
        (12, Decimal('10000.00'), 'shorter_term', 300, Decimal('18797.02'))


def test_post_calculations_422_neplatny_vstup(repository):
    """api-contract.md 422, 02a 2.3: neplatný vstup → { status: 'invalid', errors } a nič sa neuloží."""
    response = client.post('/api/calculations', json=body('12', '98238,96'))
    assert response.status_code == 422
    assert response.json() == {'status': 'invalid', 'errors': {
        'extraAmount': 'Mimoriadna splátka musí byť od 100 € a menej ako zostatok úveru 98 238,96 €.'}}
    assert repository.records == []


def test_post_calculations_422_kontrakt(repository):
    """02a 2.3: porušenie kontraktu → 422 vo formáte FastAPI { detail }."""
    response = client.post('/api/calculations', json={'amount': '100 000'})
    assert response.status_code == 422
    assert 'detail' in response.json()
    assert repository.records == []


def test_post_calculations_ignoruje_vysledky_klienta(repository):
    """AD-V2-12: výsledky z frontendu sa nedajú poslať – neznámy kľúč → 422, nič sa neuloží."""
    json = body() | {'monthly': '1,00 €'}
    assert client.post('/api/calculations', json=json).status_code == 422
    assert repository.records == []


def test_post_calculations_503(failing):
    """api-contract.md 503: Supabase neodpovedá → { error: 'storage_unavailable' }."""
    response = client.post('/api/calculations', json=body())
    assert response.status_code == 503
    assert response.json() == {'error': 'storage_unavailable'}


def test_calculate_neuklada(repository):
    """AD-V2-15: POST /api/calculate do databázy nezapisuje."""
    for _ in range(3):
        assert client.post('/api/calculate', json=body('12', '10 000')).status_code == 200
    assert repository.records == []


def test_calculate_funguje_aj_bez_databazy(failing):
    """AD-V2-15, NFR-V2-07: výpočet nepotrebuje úložisko, ani keď je nedostupné."""
    response = client.post('/api/calculate', json=body())
    assert response.status_code == 200
    assert response.json()['results']['monthly'] == '477,42 €'


# --- GET /api/calculations (FR-11) --------------------------------------------------------------

def test_get_calculations_prazdny():
    """FR-11, api-contract.md 200: prázdne úložisko → { items: [] }."""
    response = client.get('/api/calculations')
    assert response.status_code == 200
    assert response.json() == {'items': []}


def test_get_calculations_20_z_25(repository):
    """FR-11: 25 uložení → 20 najnovších, od najnovšieho."""
    ids = [client.post('/api/calculations', json=body(years=str(y))).json()['id'] for y in range(1, 26)]
    items = client.get('/api/calculations').json()['items']
    assert [i['id'] for i in items] == ids[::-1][:20]
    assert items[0]['years'] == '25 rokov' and items[-1]['years'] == '6 rokov'


def test_get_calculations_tvar_savedcalculation(repository):
    """FR-11, api-contract.md SavedCalculation: hotové texty, camelCase, extra ako text alebo null."""
    created = datetime(2026, 10, 15, 12, 5, tzinfo=UTC)
    values = SavedValues(Decimal('100000.00'), Decimal('4.00'), 30, Decimal('477.42'), Decimal('171869.51'),
                         Decimal('71869.51'))
    repository.records.append(SavedRecord(id='a', created_at=created, values=values))
    client.post('/api/calculations', json=body('12', '10 000', 'lower_payment', amount='150 000', rate='3,5',
                                               years='2'))
    first, second = client.get('/api/calculations').json()['items']
    assert second == {'id': 'a', 'createdAt': '15. 10. 2026 14:05', 'amount': '100 000,00 €', 'rate': '4,00 %',
                      'years': '30 rokov', 'monthly': '477,42 €', 'extra': None}
    assert {k: first[k] for k in ('amount', 'rate', 'years', 'monthly', 'extra')} == {
        'amount': '150 000,00 €', 'rate': '3,50 %', 'years': '2 roky', 'monthly': '6 480,41 €',
        'extra': '10 000,00 € v 12. mesiaci, nižšia splátka'}


def test_get_calculations_po_ulozeni_prvy(repository):
    """FR-10: nový záznam je v zozname ako prvý."""
    repository.records.append(SavedRecord('old', datetime.now(UTC) - timedelta(days=1), SavedValues(
        Decimal('1000.00'), Decimal('0.00'), 1, Decimal('83.33'), Decimal('1000.00'), Decimal('0.00'))))
    new_id = client.post('/api/calculations', json=body()).json()['id']
    assert client.get('/api/calculations').json()['items'][0]['id'] == new_id


def test_get_calculations_503(failing):
    """api-contract.md 503."""
    response = client.get('/api/calculations')
    assert response.status_code == 503
    assert response.json() == {'error': 'storage_unavailable'}


def test_openapi_4_endpointy():
    """Krok 8, Hotové keď: GET /docs (OpenAPI) ukazuje 4 endpointy."""
    paths = client.get('/openapi.json').json()['paths']
    assert {(p, m) for p, ops in paths.items() for m in ops} == {
        ('/api/calculate', 'post'), ('/api/calculations', 'post'), ('/api/calculations', 'get'),
        ('/api/health', 'get')}
