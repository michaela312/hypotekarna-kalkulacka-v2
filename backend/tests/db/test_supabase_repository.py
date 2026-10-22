"""Testy B13 SupabaseRepository – FR-10, NFR-V2-06, NFR-V2-07. Bez internetu.

Používa skutočnú knižnicu supabase, ale HTTP odpovede Supabase (PostgREST) simuluje httpx.MockTransport.
Overí sa tak presná požiadavka, ktorú by backend poslal do Supabase, aj spracovanie odpovede.
"""
import json
from datetime import UTC, datetime
from decimal import Decimal

import httpx
import pytest
from supabase import ClientOptions, create_client

from app.db.repository import StorageError
from app.db.supabase_repository import EXTRA_COLUMNS, SupabaseRepository, to_row
from app.services.calculator import SavedValues

URL = 'https://abcd.supabase.co'
KEY = 'service-role-kluc'
VALUES = SavedValues(Decimal('100000.00'), Decimal('4.00'), 30, Decimal('477.42'), Decimal('171869.51'), Decimal('71869.51'))
ROW_ID = '3f1c2b9a-0d4e-4c55-9a7e-2b6f1d0c8e11'


def repository(handler) -> SupabaseRepository:
    """SupabaseRepository so skutočným klientom supabase, ktorého HTTP vrstvu obsluhuje handler."""
    http = httpx.Client(transport=httpx.MockTransport(handler))
    options = ClientOptions(httpx_client=http, persist_session=False, auto_refresh_token=False)
    return SupabaseRepository(create_client(URL, KEY, options=options))


def created(request: httpx.Request) -> httpx.Response:
    """Odpoveď PostgREST na insert s Prefer: return=representation."""
    row = {'id': ROW_ID, 'created_at': '2026-10-15T12:05:00.123456+00:00', **json.loads(request.content)}
    return httpx.Response(201, json=[row])


def test_to_row_sumy_ako_text():
    """FR-10: sumy sa posielajú ako text s 2 desatinnými miestami, nie float (žiadna strata centov)."""
    assert to_row(VALUES) == {
        'amount': '100000.00', 'rate': '4.00', 'years': 30,
        'monthly_payment': '477.42', 'total_paid': '171869.51', 'total_interest': '71869.51',
        **dict.fromkeys(EXTRA_COLUMNS),
    }


def test_supabase_poziadavka_na_insert():
    """FR-10, NFR-V2-06: POST na /rest/v1/calculations s kľúčom service_role a riadkom podľa S1."""
    requests = []

    def handler(request):
        requests.append(request)
        return created(request)

    repository(handler).save(VALUES)

    [request] = requests
    assert request.method == 'POST'
    assert str(request.url) == f'{URL}/rest/v1/calculations'
    assert request.headers['apikey'] == KEY
    assert request.headers['authorization'] == f'Bearer {KEY}'
    assert 'return=representation' in request.headers['prefer']
    assert json.loads(request.content) == to_row(VALUES)


def test_supabase_odpoved_na_zaznam():
    """FR-10: id a created_at z odpovede Supabase sa prevedú na SavedRecord."""
    record = repository(created).save(VALUES)
    assert record.id == ROW_ID
    assert record.created_at == datetime(2026, 10, 15, 12, 5, 0, 123456, tzinfo=UTC)
    assert record.values == VALUES


def raise_timeout(request):
    raise httpx.ReadTimeout('timeout', request=request)


def raise_network(request):
    raise httpx.ConnectError('no route', request=request)


@pytest.mark.parametrize('handler', [
    pytest.param(lambda r: httpx.Response(401, json={'message': 'Invalid API key'}), id='zly_kluc_401'),
    pytest.param(lambda r: httpx.Response(400, json={'code': '23514', 'message': 'violates check constraint'}),
                 id='porusenie_check_400'),
    pytest.param(lambda r: httpx.Response(404, json={'code': '42P01', 'message': 'relation does not exist'}),
                 id='chyba_tabulka_404'),
    pytest.param(lambda r: httpx.Response(503, text='Service Unavailable'), id='pozastaveny_projekt_503 R-V2-03'),
    pytest.param(lambda r: httpx.Response(201, json=[]), id='prazdna_odpoved'),
    pytest.param(raise_timeout, id='timeout NFR-V2-07'),
    pytest.param(raise_network, id='bez_internetu'),
])
def test_supabase_chyby_su_storage_error(handler):
    """NFR-V2-07: každá chyba Supabase alebo siete je StorageError."""
    with pytest.raises(StorageError, match='Výpočet sa nepodarilo uložiť do Supabase'):
        repository(handler).save(VALUES)


def test_supabase_chyba_neprezradi_kluc():
    """NFR-V2-06: text chyby neobsahuje kľúč service_role."""
    with pytest.raises(StorageError) as err:
        repository(lambda r: httpx.Response(401, json={'message': 'Invalid API key'})).save(VALUES)
    assert KEY not in str(err.value)
