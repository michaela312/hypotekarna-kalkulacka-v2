"""Statické testy frontend/index.html – NFR-V2-04, NFR-V2-05, AD-V2-05, AD-V2-13 a pravidlo 5 v Dependency Direction.

Správanie v prehliadači (debounce, poradie odpovedí, timeout) zatiaľ overené ručne, Playwright testy pribudnú v e2e/.
"""
import re
from html.parser import HTMLParser
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app

INDEX = Path(__file__).resolve().parents[2] / 'frontend' / 'index.html'
HTML = INDEX.read_text(encoding='utf-8')
SCRIPT_WITH_COMMENTS = re.search(r'<script type="module">(.*?)</script>', HTML, re.S).group(1)
# Kód bez komentárov // a /** */, aby kontroly nenašli slová z komentárov.
SCRIPT = re.sub(r'/\*.*?\*/|//[^\n]*', '', SCRIPT_WITH_COMMENTS, flags=re.S)


class Elements(HTMLParser):
    def __init__(self):
        super().__init__()
        self.items: list[tuple[str, dict[str, str]]] = []

    def handle_starttag(self, tag, attrs):
        self.items.append((tag, {k: v or '' for k, v in attrs}))


def elements() -> list[tuple[str, dict[str, str]]]:
    parser = Elements()
    parser.feed(HTML)
    return parser.items


def test_frontend_je_jeden_subor():
    """AD-V2-13: frontend je jeden súbor index.html."""
    assert [p.name for p in INDEX.parent.iterdir()] == ['index.html']


def test_frontend_bez_externych_zdrojov():
    """NFR-V2-05: 0 načítaní z CDN alebo iných súborov (script src, link href, @import, url())."""
    for tag, attrs in elements():
        assert not (tag == 'script' and 'src' in attrs)
        assert not (tag == 'link' and attrs.get('rel') == 'stylesheet')
    assert '@import' not in HTML and 'url(' not in HTML


def test_frontend_iba_jedno_volanie_fetch():
    """Pravidlo 5, API-R1: iba F5 volá fetch(), a to iba na /api/calculate."""
    assert len(re.findall(r'\bfetch\(', SCRIPT)) == 1
    assert re.findall(r"fetch\('([^']+)'", SCRIPT) == ['/api/calculate']


def test_frontend_bez_vypoctov_a_formatovania():
    """NFR-V2-05, API-R4: žiadny vzorec, hranice vstupov ani formátovanie čísel."""
    for forbidden in ('Math.', 'toFixed', 'Intl.', 'toLocaleString', 'parseFloat', 'parseInt', 'Number('):
        assert forbidden not in SCRIPT


def test_frontend_polia_maju_label():
    """NFR-V2-04: každé pole má <label for> a type="text" (AD-03 V1)."""
    items = elements()
    inputs = [a for t, a in items if t == 'input']
    labels = {a['for'] for t, a in items if t == 'label'}
    assert [a['data-field'] for a in inputs] == ['amount', 'rate', 'years']
    for attrs in inputs:
        assert attrs['type'] == 'text'
        assert attrs['id'] in labels


def test_frontend_predvyplnene_hodnoty():
    """AD-08 V1: polia sú predvyplnené 100 000 / 4 / 30."""
    values = [a['value'] for t, a in elements() if t == 'input']
    assert values == ['100 000', '4', '30']


def test_frontend_casove_limity():
    """NFR-V2-01 (debounce 300 ms), API-R7 (timeout 5 s)."""
    assert 'const DEBOUNCE_MS = 300;' in SCRIPT
    assert 'const TIMEOUT_MS = 5000;' in SCRIPT


def test_backend_servíruje_frontend():
    """AD-V2-05, NFR-V2-08: GET / vráti index.html z toho istého servera ako API."""
    response = TestClient(app).get('/')
    assert response.status_code == 200
    assert response.headers['content-type'].startswith('text/html')
    assert '<title>Hypotekárna kalkulačka</title>' in response.text
