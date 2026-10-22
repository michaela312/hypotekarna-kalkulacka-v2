"""Testy B10, B11 – POST /api/calculate (FR-01 až FR-05, API-R1 až API-R6, NFR-V2-02) a GET /api/health."""
import statistics
import time

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

NO_EXTRA = {'extra': {'month': '', 'amount': '', 'mode': 'shorter_term'}}


def test_api_vypocet_referencny_priklad():
    """FR-01 až FR-04, API-R4: hotové texty, extra = null."""
    response = client.post('/api/calculate', json={'amount': '100 000', 'rate': '4', 'years': '30', **NO_EXTRA})
    assert response.status_code == 200
    assert response.json() == {
        'status': 'ok',
        'results': {'monthly': '477,42 €', 'total': '171 869,51 €', 'interest': '71 869,51 €', 'extra': None},
    }


def test_api_neplatny_vstup_je_200():
    """FR-05, API-R5: neplatný vstup je HTTP 200 so status 'invalid' a bez results."""
    response = client.post('/api/calculate', json={'amount': '100000', 'rate': '', 'years': '2,5', **NO_EXTRA})
    assert response.status_code == 200
    assert response.json() == {
        'status': 'invalid',
        'errors': {
            'rate': 'Ročná úroková sadzba musí byť od 0 do 20 %.',
            'years': 'Doba splácania musí byť od 1 do 30 rokov.',
        },
    }


@pytest.mark.parametrize('body', [
    pytest.param({'amount': '100000', 'rate': '4'}, id='chyba_kluc'),
    pytest.param({'amount': 100000, 'rate': '4', 'years': '30', **NO_EXTRA}, id='cislo_namiesto_textu API-R3'),
    pytest.param({'amount': '100000', 'rate': '4', 'years': '30', 'foo': '1', **NO_EXTRA}, id='neznamy_kluc'),
])
def test_api_porusenie_kontraktu_je_422(body):
    """API-R6"""
    assert client.post('/api/calculate', json=body).status_code == 422


def test_api_health():
    """NFR-V2-08"""
    response = client.get('/api/health')
    assert response.status_code == 200
    assert response.json() == {'status': 'ok'}


def test_api_cas_odpovede():
    """NFR-V2-02: medián zo 100 volaní ≤ 50 ms, s mimoriadnou splátkou v mesiaci 1 pri 30 rokoch."""
    body = {'amount': '1 000 000', 'rate': '20', 'years': '30',
            'extra': {'month': '1', 'amount': '100', 'mode': 'shorter_term'}}
    durations = []
    for _ in range(100):
        start = time.perf_counter()
        client.post('/api/calculate', json=body)
        durations.append(time.perf_counter() - start)
    assert statistics.median(durations) <= 0.050


# --- Automatické uloženie (FR-10, AD-V2-14) -----------------------------------------------------

VALID = {'amount': '100 000', 'rate': '4', 'years': '30', **NO_EXTRA}


def test_api_platny_vypocet_sa_ulozi(repository):
    """FR-10, AD-V2-14: platný výpočet sa uloží 1× so zaokrúhlenými hodnotami (AD-V2-08)."""
    client.post('/api/calculate', json=VALID)
    [record] = repository.records
    values = record.values
    assert (str(values.amount), str(values.rate), values.years) == ('100000.00', '4.00', 30)
    assert (str(values.monthly_payment), str(values.total_paid), str(values.total_interest)) == \
        ('477.42', '171869.51', '71869.51')


def test_api_kazdy_vypocet_je_novy_zaznam(repository):
    """AD-V2-14: každé volanie s platným vstupom = 1 nový riadok, aj pri rovnakých hodnotách."""
    for _ in range(3):
        client.post('/api/calculate', json=VALID)
    assert len(repository.records) == 3


def test_api_neplatny_vstup_sa_neulozi(repository):
    """FR-05: neplatný vstup sa neukladá."""
    client.post('/api/calculate', json={'amount': '999', 'rate': '4', 'years': '30', **NO_EXTRA})
    assert repository.records == []


def test_api_porusenie_kontraktu_sa_neulozi(repository):
    """API-R6: pri 422 sa nič neukladá."""
    client.post('/api/calculate', json={'amount': '100000'})
    assert repository.records == []


def test_api_chyba_databazy_nepokazi_vypocet(caplog):
    """NFR-V2-07: keď Supabase neodpovedá, výpočet sa aj tak zobrazí a chyba sa zapíše do logu."""
    from app.api.routes import get_repository
    from app.db.repository import InMemoryRepository
    app.dependency_overrides[get_repository] = lambda: InMemoryRepository(fail=True)

    response = client.post('/api/calculate', json=VALID)

    assert response.status_code == 200
    assert response.json()['results']['monthly'] == '477,42 €'
    assert 'Pamäťové úložisko je nastavené na chybu.' in caplog.text
