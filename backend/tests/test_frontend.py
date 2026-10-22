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


def text_inputs() -> list[dict[str, str]]:
    return [a for t, a in elements() if t == 'input' and a.get('type') != 'radio']


def test_frontend_polia_maju_label():
    """NFR-V2-04: každé textové pole má <label for> a type="text" (AD-03 V1)."""
    labels = {a['for'] for t, a in elements() if t == 'label' and 'for' in a}
    inputs = text_inputs()
    assert [a['data-field'] for a in inputs] == ['amount', 'rate', 'years', 'extraMonth', 'extraAmount']
    for attrs in inputs:
        assert attrs['type'] == 'text'
        assert attrs['id'] in labels


def test_frontend_predvyplnene_hodnoty():
    """AD-08 V1: polia sú predvyplnené 100 000 / 4 / 30, IN-04 a IN-05 prázdne."""
    assert [a['value'] for a in text_inputs()] == ['100 000', '4', '30', '', '']


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


def test_frontend_posiela_extra():
    """API-R6: readForm() posiela povinný kľúč extra s month, amount a mode."""
    read_form = re.search(r'function readForm\(\) \{(.*?)\n    \}', SCRIPT, re.S).group(1)
    assert 'extra:' in read_form
    for key in ('month', 'amount', 'mode'):
        assert key in read_form


# --- Krok 9: mimoriadna splátka (FR-06 až FR-09, IN-04 až IN-06) -------------------------------

FIELDSET = re.search(r'<fieldset>(.*?)</fieldset>\s*</form>', HTML, re.S).group(1)


def test_nfr_v2_04_fieldset_legend():
    """NFR-V2-04: IN-04 až IN-06 sú vo <fieldset> s <legend>, prepínač IN-06 vo vlastnom <fieldset> s <legend>."""
    assert '<legend>Mimoriadna splátka</legend>' in FIELDSET
    assert 'data-field="extraMonth"' in FIELDSET and 'data-field="extraAmount"' in FIELDSET
    modes = re.search(r'<fieldset class="modes">(.*?)</fieldset>', FIELDSET, re.S).group(1)
    assert '<legend>' in modes and modes.count('type="radio"') == 2


def test_nfr_v2_04_kazdy_vstup_ma_label():
    """NFR-V2-04: 5 textových polí má <label for> a 2 prepínače sú vnorené v <label> s textom."""
    labels = {a['for'] for t, a in elements() if t == 'label' and 'for' in a}
    assert {a['id'] for a in text_inputs()} <= labels
    radio_labels = re.findall(r'<label><input type="radio" name="mode" value="(\w+)"[^>]*> ([^<]+)</label>', HTML)
    assert radio_labels == [('shorter_term', 'Kratšia doba'), ('lower_payment', 'Nižšia splátka')]


def test_nfr_v2_05_ziadne_cisla_hranic():
    """NFR-V2-05: skript neobsahuje hranice vstupov (359, 100, 1000000, 1 000 000) ani vzorce."""
    for number in ('359', '100', '1000000', '1 000 000', '1_000_000'):
        assert not re.search(rf'(?<![\d_]){re.escape(number)}(?![\d_])', SCRIPT), number


def test_nfr_v2_05_ziadne_externe_zdroje():
    """NFR-V2-05: 0 importov v skripte (žiadne import/require/eval)."""
    assert not re.search(r'import|require\(|eval\(', SCRIPT)


def test_frontend_data_atributy_extra():
    """02a 1.3: atribúty data-* pre FR-06 až FR-09."""
    for name in ('extraMonth', 'extraAmount'):
        assert f'data-field="{name}"' in HTML and f'data-error="{name}"' in HTML
    for key in ('payments', 'lastPayment', 'newMonthly', 'total', 'interest', 'interestSaved'):
        assert f'data-result="extra.{key}"' in HTML
    assert 'data-extra-mode' in HTML


def test_frontend_predvoleny_rezim():
    """IN-06, OQ-V2-03: predvolený režim je Kratšia doba (checked)."""
    checked = [a['value'] for t, a in elements() if t == 'input' and a.get('type') == 'radio' and 'checked' in a]
    assert checked == ['shorter_term']


def test_frontend_zmena_rezimu_spusti_vypocet():
    """IN-06: zmena prepínača (udalosť change) naplánuje výpočet."""
    assert re.search(r"addEventListener\('change'.*?name === 'mode'.*?schedule\(", SCRIPT, re.S)
