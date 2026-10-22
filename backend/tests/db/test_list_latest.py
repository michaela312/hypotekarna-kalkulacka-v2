"""Testy B12 a B13 – list_latest a stĺpce extra_* (krok 7 docs/v2/05-plan.md). FR-10, FR-11, NFR-V2-07. Bez internetu."""
import json
from datetime import UTC, datetime
from decimal import Decimal
from urllib.parse import parse_qs

import httpx
import pytest
from supabase import ClientOptions, create_client

from app.db.repository import InMemoryRepository, StorageError
from app.db.supabase_repository import EXTRA_COLUMNS, SupabaseRepository, from_row, to_row
from app.services.calculator import SavedExtra, SavedValues

URL = 'https://abcd.supabase.co'
KEY = 'service-role-kluc'
BASE = SavedValues(Decimal('100000.00'), Decimal('4.00'), 30, Decimal('477.42'), Decimal('171869.51'),
                   Decimal('71869.51'))
SHORTER = SavedValues(**{**BASE.__dict__, 'extra': SavedExtra(
    month=12, amount=Decimal('10000.00'), mode='shorter_term', payments=300, last_payment=Decimal('325.32'),
    new_monthly=None, total_paid=Decimal('153072.49'), total_interest=Decimal('53072.49'),
    interest_saved=Decimal('18797.02'))})
LOWER = SavedValues(**{**BASE.__dict__, 'extra': SavedExtra(
    month=12, amount=Decimal('10000.00'), mode='lower_payment', payments=None, last_payment=None,
    new_monthly=Decimal('428.82'), total_paid=Decimal('164957.63'), total_interest=Decimal('64957.63'),
    interest_saved=Decimal('6911.88'))})


def repository(handler) -> SupabaseRepository:
    http = httpx.Client(transport=httpx.MockTransport(handler))
    options = ClientOptions(httpx_client=http, persist_session=False, auto_refresh_token=False)
    return SupabaseRepository(create_client(URL, KEY, options=options))


def db_row(values: SavedValues, row_id: str = 'id-1', created_at: str = '2026-10-15T12:05:00+00:00') -> dict:
    """Riadok tak, ako ho vráti PostgREST: numeric ako číslo JSON, nie text."""
    row = {'id': row_id, 'created_at': created_at}
    for key, value in to_row(values).items():
        row[key] = float(value) if isinstance(value, str) and key != 'extra_mode' else value
    return row


# --- B12 InMemoryRepository ---------------------------------------------------------------------

def test_inmemory_list_latest_20_z_25():
    """FR-11: 25 uložených → 20 najnovších, 5 najstarších chýba."""
    repo = InMemoryRepository()
    saved = [repo.save(BASE) for _ in range(25)]
    assert repo.list_latest() == saved[::-1][:20]


def test_inmemory_list_poradie():
    """FR-11: od najnovšieho; prázdne úložisko vráti []."""
    repo = InMemoryRepository()
    assert repo.list_latest() == []
    first, second = repo.save(BASE), repo.save(SHORTER)
    assert repo.list_latest() == [second, first]
    assert repo.list_latest(limit=1) == [second]


def test_inmemory_fail():
    """AD-V2-09: InMemoryRepository(fail=True) vyhodí StorageError aj pri čítaní."""
    with pytest.raises(StorageError):
        InMemoryRepository(fail=True).list_latest()


# --- B13 to_row / from_row ----------------------------------------------------------------------

def test_to_row_17_stlpcov_bez_id_a_created_at():
    """S1: riadok má 15 stĺpcov = 17 stĺpcov tabuľky bez id a created_at (tie vytvorí databáza)."""
    row = to_row(SHORTER)
    assert len(row) == 15
    assert 'id' not in row and 'created_at' not in row


def test_to_row_extra_null_vsetky_extra_none():
    """S1 constraint extra_all_or_nothing: bez mimoriadnej splátky sú všetky extra_* None."""
    row = to_row(BASE)
    assert [row[c] for c in EXTRA_COLUMNS] == [None] * 9


@pytest.mark.parametrize('values, expected', [
    pytest.param(SHORTER, {'extra_month': 12, 'extra_amount': '10000.00', 'extra_mode': 'shorter_term',
                           'extra_payments': 300, 'extra_last_payment': '325.32', 'extra_new_monthly': None,
                           'extra_total_paid': '153072.49', 'extra_total_interest': '53072.49',
                           'extra_interest_saved': '18797.02'}, id='kratsia_doba FR-06'),
    pytest.param(LOWER, {'extra_month': 12, 'extra_amount': '10000.00', 'extra_mode': 'lower_payment',
                         'extra_payments': None, 'extra_last_payment': None, 'extra_new_monthly': '428.82',
                         'extra_total_paid': '164957.63', 'extra_total_interest': '64957.63',
                         'extra_interest_saved': '6911.88'}, id='nizsia_splatka FR-07'),
])
def test_to_row_sumy_ako_text(values, expected):
    """FR-10: 9 stĺpcov extra_* podľa DR-10 riadku 1; sumy ako text s 2 desatinnými miestami."""
    row = to_row(values)
    assert {c: row[c] for c in EXTRA_COLUMNS} == expected


@pytest.mark.parametrize('values', [BASE, SHORTER, LOWER], ids=['bez_extra', 'kratsia_doba', 'nizsia_splatka'])
def test_from_row_round_trip(values):
    """FR-11: riadok z databázy (numeric ako číslo JSON) → SavedRecord s rovnakými hodnotami."""
    record = from_row(db_row(values))
    assert record.values == values
    assert record.id == 'id-1'
    assert record.created_at == datetime(2026, 10, 15, 12, 5, tzinfo=UTC)


def test_from_row_cele_cislo_ma_2_desatinne():
    """FR-11: PostgREST vráti 100000 namiesto 100000.00 → Decimal('100000.00')."""
    row = db_row(BASE) | {'amount': 100000, 'rate': 4}
    values = from_row(row).values
    assert (str(values.amount), str(values.rate)) == ('100000.00', '4.00')


# --- B13 list_latest cez HTTP (MockTransport) ---------------------------------------------------

def test_list_latest_url_a_parametre():
    """FR-11, NFR-V2-06: GET /rest/v1/calculations?select=*&order=created_at.desc&limit=20 s kľúčom service_role."""
    requests = []

    def handler(request):
        requests.append(request)
        return httpx.Response(200, json=[db_row(SHORTER, 'b'), db_row(BASE, 'a')])

    records = repository(handler).list_latest()

    [request] = requests
    assert request.method == 'GET'
    assert request.url.path == '/rest/v1/calculations'
    assert parse_qs(request.url.query.decode()) == {'select': ['*'], 'order': ['created_at.desc'], 'limit': ['20']}
    assert request.headers['apikey'] == KEY
    assert [r.id for r in records] == ['b', 'a']
    assert records[0].values == SHORTER


def test_list_latest_prazdna_tabulka():
    """FR-11: prázdna tabuľka → []."""
    assert repository(lambda r: httpx.Response(200, json=[])).list_latest() == []


def raise_timeout(request):
    raise httpx.ReadTimeout('timeout', request=request)


def raise_network(request):
    raise httpx.ConnectError('no route', request=request)


@pytest.mark.parametrize('handler', [
    pytest.param(lambda r: httpx.Response(401, json={'message': 'Invalid API key'}), id='zly_kluc_401'),
    pytest.param(lambda r: httpx.Response(404, json={'code': '42P01', 'message': 'relation does not exist'}),
                 id='chyba_tabulka_404'),
    pytest.param(lambda r: httpx.Response(400, json={'code': '42703', 'message': 'column does not exist'}),
                 id='chyba_stlpec_400'),
    pytest.param(lambda r: httpx.Response(503, text='Service Unavailable'), id='pozastaveny_projekt_503 R-V2-03'),
    pytest.param(lambda r: httpx.Response(200, json=[{'id': 'x'}]), id='neocakavany_tvar_riadku'),
    pytest.param(raise_timeout, id='timeout NFR-V2-07'),
    pytest.param(raise_network, id='bez_internetu'),
])
def test_list_latest_chyby(handler):
    """NFR-V2-07: každá chyba pri čítaní je StorageError a neprezradí kľúč."""
    with pytest.raises(StorageError, match='Uložené výpočty sa nepodarilo načítať') as err:
        repository(handler).list_latest()
    assert KEY not in str(err.value)


def test_save_s_extra_posle_vsetky_stlpce():
    """FR-10: insert s mimoriadnou splátkou pošle 15 stĺpcov vrátane 9 extra_*."""
    sent = []

    def handler(request):
        sent.append(json.loads(request.content))
        return httpx.Response(201, json=[{'id': 'x', 'created_at': '2026-10-15T12:05:00+00:00', **sent[-1]}])

    repository(handler).save(SHORTER)
    assert sent == [to_row(SHORTER)]


def test_list_latest_503_bez_opakovania():
    """NFR-V2-07: pri 503 sa GET neopakuje (postgrest by čakal ~7 s) – 1 požiadavka, odpoveď do 1 s."""
    requests = []

    def handler(request):
        requests.append(request)
        return httpx.Response(503, text='Service Unavailable')

    start = datetime.now()
    with pytest.raises(StorageError):
        repository(handler).list_latest()
    assert len(requests) == 1
    assert (datetime.now() - start).total_seconds() < 1
