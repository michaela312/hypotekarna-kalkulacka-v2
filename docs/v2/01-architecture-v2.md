# Architektúra V2 po vrstvách – implementačný pohľad

Tento dokument opisuje 4 vrstvy V2 tak, aby sa podľa neho dalo priamo programovať: frontend, API kontrakt, backend a Supabase.
Nezavádza nové požiadavky ani rozhodnutia. Zdroje pravdy zostávajú:

| Téma | Zdroj pravdy | Čo pridáva tento dokument |
|------|--------------|---------------------------|
| Požiadavky FR, IN, DR | `01-functional.md` | – |
| Moduly B1–B15, F1–F5, S1, NFR, AD | `02-architecture.md` | Rozdelenie podľa vrstiev, atribúty DOM, stavy UI, kostry kódu |
| Tvar JSON a HTTP kódy | `api-contract.md` | Kompletné príklady pre každý prípad, Pydantic modely |
| Tabuľka `calculations` (SQL) | `02-architecture.md`, časť Data Model → S1 | Mapovanie stĺpcov, pripojenie, postup založenia projektu |

Ak sa tento dokument a zdroj pravdy líšia, platí zdroj pravdy a tento dokument sa opraví.

```
┌────────────────────┐  JSON   ┌──────────────────┐  volanie  ┌─────────────────────┐  HTTPS  ┌───────────┐
│ 1. Frontend (JS)   │ ──────► │ 2. API kontrakt  │ ────────► │ 3. Backend (FastAPI)│ ──────► │ 4. Supabase│
│ frontend/          │ ◄────── │ /api/*, B10      │ ◄──────── │ backend/app/        │ ◄────── │ calculations│
└────────────────────┘ texty   └──────────────────┘           └─────────────────────┘         └───────────┘
   F1–F5                          API-R1–API-R7                  B1–B15                        S1
```

Všetko beží lokálne na `http://127.0.0.1:8000/` jedným príkazom (NFR-V2-08). Backend servíruje aj frontend (AD-V2-05).

---

## 1. Frontend (JavaScript)

### 1.1 Úloha
- Čítať surové texty z formulára a posielať ich na API (API-R3).
- Vykresliť hotové texty z odpovede (API-R4).
- Nič nepočíta, nevaliduje, neformátuje a nepozná hranice vstupov (NFR-V2-05).

### 1.2 Súbory a zodpovednosti

**Zmena (AD-V2-13):** frontend je jeden súbor `frontend/index.html`. Tabuľka nižšie platí pre oddiely v ňom, nie pre samostatné súbory. Atribúty a stavy pre mimoriadnu splátku a ukladanie (1.3, 1.4) pribudnú s B6, FR-10 a FR-11.

| Modul | Súbor | Robí | Nesmie |
|-------|-------|------|--------|
| F1 | `frontend/index.html` | Markup formulára, výsledkov, tlačidla a zoznamu | Obsahovať inline JS |
| F2 | `frontend/styles.css` | Vzhľad, sumy sa nezalomia (FR-04) | – |
| F3 | `frontend/js/main.js` | Debounce 300 ms, poradie požiadaviek, riadenie uloženia | Volať `fetch()` alebo `document` |
| F4 | `frontend/js/view.js` | `readForm()`, `render()`, `renderList()`, `setSaveState()` | Volať `fetch()` |
| F5 | `frontend/js/api.js` | `calculate()`, `saveCalculation()`, `listCalculations()` | Používať `document` |

Načítanie: `<script type="module" src="js/main.js"></script>`. 0 balíkov z npm, 0 načítaní z CDN (NFR-V2-05).

### 1.3 Väzba na DOM (F1 ↔ F4)

Rozšírenie atribútov z M11 V1 (`docs/v1/02-architecture.md`). F4 hľadá prvky iba cez tieto atribúty.

| Prvok | Atribút | Hodnoty | Požiadavka |
|-------|---------|---------|------------|
| Vstupné pole (`type="text"`) | `data-field` | `amount`, `rate`, `years`, `extraMonth`, `extraAmount` | IN-01 až IN-05 |
| Prepínač režimu (2× `type="radio"`) | `name="mode"` | `shorter_term` (predvolené, `checked`), `lower_payment` | IN-06 |
| Chybová správa poľa | `data-error` | rovnaké hodnoty ako `data-field` | FR-05, FR-09 |
| Základný výsledok | `data-result` | `monthly`, `total`, `interest` | FR-01 až FR-03 |
| Výsledok mimoriadnej splátky | `data-result` | `extra.payments`, `extra.lastPayment`, `extra.newMonthly`, `extra.total`, `extra.interest`, `extra.interestSaved` | FR-06 až FR-08 |
| Kontajner výsledku mimoriadnej splátky | `data-extra-mode` | `shorter_term`, `lower_payment` | FR-06, FR-07 |
| Tlačidlo „Uložiť výpočet“ | `data-action="save"` | – | FR-10 |
| Správa uloženia | `data-status="save"`, `role="status"` | – | FR-10, NFR-V2-04 |
| Telo tabuľky zoznamu | `data-list="calculations"` | – | FR-11 |
| Správa zoznamu | `data-status="list"` | – | FR-11 |

Predvyplnené hodnoty pri načítaní: `amount = "100 000"`, `rate = "4"`, `years = "30"`, IN-04 a IN-05 prázdne (AD-08 V1).

Polia vo formulári sú `<input type="text" inputmode="decimal">`, nie `type="number"` (AD-03 V1), aby sa do API dostal presne zadaný text.

### 1.4 Stavy UI

| Stav | Kedy | Výsledky | Chyby polí | Tlačidlo „Uložiť“ |
|------|------|----------|------------|-------------------|
| `ok` | Odpoveď `status: 'ok'` | zobrazené; blok `extra` iba ak `results.extra !== null` | skryté, `aria-invalid` odstránené | aktívne |
| `invalid` | Odpoveď `status: 'invalid'` | všetky skryté (FR-05, FR-09) | zobrazené pri kľúčoch z `errors`, `aria-invalid="true"` | neaktívne |
| `unavailable` | `ApiError` z `calculate()` | predchádzajúce skryté | skryté | neaktívne |
| `saving` | Po kliknutí na „Uložiť“, do odpovede | bez zmeny | bez zmeny | neaktívne (FR-10: 1 klik = najviac 1 záznam) |

Pre stav `unavailable` nie je text vo FR. Návrh: „Výpočet je dočasne nedostupný. Skúste to znova.“ – doplniť do `01-functional.md` pri review (04).

### 1.5 Tok v F3

```
načítanie stránky
  ├─► scheduleCalculate(0 ms)            # okamžitý výpočet predvyplnených hodnôt
  └─► refreshList()

udalosť 'input' alebo 'change' na formulári
  └─► scheduleCalculate(300 ms)          # AD-V2-02, NFR-V2-01

scheduleCalculate(delay):
  zruš predchádzajúci časovač
  po delay: seq = ++lastSeq
            res = await api.calculate(view.readForm())
            if seq !== lastSeq: zahoď              # R-V2-04, staršia odpoveď
            view.render(res)

klik na data-action="save":
  view.setSaveState('saving')
  res = await api.saveCalculation(view.readForm())
  ApiError  → view.showSaveMessage('Výpočet sa nepodarilo uložiť. Skúste to znova.')
  inak      → view.showSaveMessage('Výpočet bol uložený.'); refreshList()
  view.setSaveState(podľa posledného render)

refreshList():
  res = await api.listCalculations()
  ApiError       → 'Uložené výpočty sa nepodarilo načítať.'
  items.length 0 → 'Zatiaľ nie sú uložené žiadne výpočty.'
  inak           → view.renderList(items)
```

### 1.6 Klient API (F5)

```js
// frontend/js/api.js – F5, implementuje API-R1, API-R7
const TIMEOUT_MS = 5000;

/** @returns {Promise<{ok: true, status: number, body: any} | {error: 'network'|'timeout'|'storage'|'contract'}>} */
async function request(method, path, body) { /* fetch + AbortController(TIMEOUT_MS) */ }

export async function calculate(req)       { /* POST /api/calculate    → CalculationResponse | ApiError */ }
export async function saveCalculation(req) { /* POST /api/calculations → { id, createdAt } | ApiError */ }
export async function listCalculations()   { /* GET  /api/calculations → { items }         | ApiError */ }
```

Prevod HTTP na výsledok F5:

| Situácia | Výsledok F5 |
|----------|-------------|
| 200 / 201 | telo odpovede |
| 503 | `{ error: 'storage' }` |
| 422 | `{ error: 'contract' }` – chyba vo frontende; zapíše sa `console.error` s telom |
| `TypeError` z `fetch` | `{ error: 'network' }` |
| `AbortError` po 5 000 ms | `{ error: 'timeout' }` |

F5 nikdy nevyhodí výnimku. F3 rozlišuje iba „telo“ vs. „ApiError“.

### 1.7 Testy frontendu
- Playwright v `e2e/`, backend spustený so `STORAGE=memory` (B14).
- Spomalenie odpovede pre R-V2-04 a timeout pre API-R7 sa simuluje cez `page.route()`.
- Každý test uvádza ID (napr. `test('FR-10: 1 klik = 1 záznam', …)`).

---

## 2. API kontrakt (JSON)

Typy, pravidlá API-R1 až API-R7 a HTTP kódy sú v `api-contract.md`. Táto časť dopĺňa kompletné príklady pre všetky prípady, ktoré musí implementácia a testy pokryť.

### 2.1 Prehľad endpointov

| Metóda a cesta | Požiadavka | Úspech | Chyby | Zapisuje do DB | Požiadavky |
|----------------|------------|--------|-------|----------------|------------|
| `POST /api/calculate` | `CalculationRequest` | 200 `CalculationResponse` | 422 kontrakt | nie (AD-V2-07) | FR-01 až FR-09 |
| `POST /api/calculations` | `CalculationRequest` | 201 `{ id, createdAt }` | 422 neplatný vstup alebo kontrakt, 503 | áno, 1 riadok | FR-10 |
| `GET /api/calculations` | – | 200 `{ items: SavedCalculation[] }` (0 až 20) | 503 | nie | FR-11 |
| `GET /api/health` | – | 200 `{ "status": "ok" }` | – | nie | NFR-V2-08 |

### 2.2 `POST /api/calculate` – príklady

**A. Bez mimoriadnej splátky** (IN-04 aj IN-05 prázdne → `extra: null`, FR-09):
```json
{ "amount": "100 000", "rate": "4", "years": "30",
  "extra": { "month": "", "amount": "", "mode": "shorter_term" } }
```
```json
{ "status": "ok",
  "results": { "monthly": "477,42 €", "total": "171 869,51 €", "interest": "71 869,51 €", "extra": null } }
```

**B. Kratšia doba** (FR-06, DR-10 riadok 1): požiadavka a odpoveď sú v `api-contract.md`, endpoint `POST /api/calculate`.

**C. Nižšia splátka** (FR-07, DR-10 riadok 1):
```json
{ "amount": "100 000", "rate": "4", "years": "30",
  "extra": { "month": "12", "amount": "10 000", "mode": "lower_payment" } }
```
```json
{ "status": "ok",
  "results": {
    "monthly": "477,42 €", "total": "171 869,51 €", "interest": "71 869,51 €",
    "extra": { "mode": "lower_payment", "newMonthly": "428,82 €",
               "total": "164 957,63 €", "interest": "64 957,63 €", "interestSaved": "6 911,88 €" } } }
```

**D. Neplatná mimoriadna splátka voči zostatku** (FR-09, riadok 2 tabuľky správ):
```json
{ "amount": "100 000", "rate": "4", "years": "30",
  "extra": { "month": "12", "amount": "98238,96", "mode": "shorter_term" } }
```
```json
{ "status": "invalid",
  "errors": { "extraAmount": "Mimoriadna splátka musí byť od 100 € a menej ako zostatok úveru 98 238,96 €." } }
```

**E. Vyplnené iba jedno pole** (FR-09, posledný riadok tabuľky správ): `"month": "12", "amount": ""` → `errors` obsahuje iba `extraAmount` so správou „Mimoriadna splátka musí byť od 100 € a menej ako zostatok úveru 98 238,96 €.“

**F. Porušenie kontraktu** (API-R6): `"mode": "faster"` alebo chýbajúci kľúč `extra` → HTTP 422 s telom, ktoré vytvorí FastAPI (`{ "detail": [ … ] }`).

### 2.3 Dva tvary tela pri 422

| Endpoint | Príčina | Telo |
|----------|---------|------|
| oba `POST` | Porušenie kontraktu (Pydantic) | `{ "detail": [ … ] }` – formát FastAPI |
| `POST /api/calculations` | Neplatný vstup používateľa | `{ "status": "invalid", "errors": { … } }` |

F5 obe vráti ako `ApiError`. Testy B11 overujú oba tvary zvlášť.

### 2.4 Pydantic modely (B10)

Kostra pre `backend/app/api/schemas.py`. Kľúče v Pythone sú `snake_case`, v JSON `camelCase` (API-R2).

```python
# B10 – implementuje API-R1 až API-R6
from typing import Literal
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

Mode = Literal['shorter_term', 'lower_payment']                 # IN-06
FieldKey = Literal['amount', 'rate', 'years', 'extraMonth', 'extraAmount']

class ApiModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, extra='forbid')

class ExtraInput(ApiModel):
    month: str                                                  # IN-04, surový text
    amount: str                                                 # IN-05, surový text
    mode: Mode

class CalculationRequest(ApiModel):
    amount: str; rate: str; years: str                          # IN-01 až IN-03
    extra: ExtraInput

class ShorterTermResult(ApiModel):                              # FR-06, FR-08
    mode: Literal['shorter_term']
    payments: str; last_payment: str
    total: str; interest: str; interest_saved: str

class LowerPaymentResult(ApiModel):                             # FR-07, FR-08
    mode: Literal['lower_payment']
    new_monthly: str
    total: str; interest: str; interest_saved: str

class Results(ApiModel):                                        # FR-01 až FR-03
    monthly: str; total: str; interest: str
    extra: ShorterTermResult | LowerPaymentResult | None

class OkResponse(ApiModel):
    status: Literal['ok']; results: Results

class InvalidResponse(ApiModel):                                # FR-05, FR-09
    status: Literal['invalid']; errors: dict[FieldKey, str]

CalculationResponse = OkResponse | InvalidResponse

class SaveResponse(ApiModel):                                   # FR-10
    id: str; created_at: str

class SavedCalculation(ApiModel):                               # FR-11
    id: str; created_at: str; amount: str; rate: str; years: str
    monthly: str; extra: str | None

class CalculationList(ApiModel):
    items: list[SavedCalculation]

class StorageErrorBody(ApiModel):
    error: Literal['storage_unavailable']
```

Odpovede sa serializujú s `by_alias=True` (v FastAPI predvolené pri `response_model`).
`extra='forbid'` zabezpečí, že neznámy kľúč vráti 422 (API-R6).

---

## 3. Backend (Python, FastAPI)

### 3.1 Vrstvy vnútri backendu

```
HTTP ─► B11 routes.py ─► B9 calculator.py ─► B1–B8 (čistý Python, NFR-V2-03)
            │
            └─► B12 CalculationRepository ◄── B13 SupabaseRepository ─► Supabase
                                         ◄── InMemoryRepository (testy, e2e)
B14 main.py: skladá B11, B12/B13, B15 a StaticFiles(frontend/)
```

Výpočet (B1–B9) nepozná HTTP ani databázu. Overí to test importov (pravidlo 7 v `02-architecture.md`).

### 3.2 Výpočtové jadro (B1–B9)

| Krok v B9 | Modul | Vstup → výstup | Požiadavky |
|-----------|-------|----------------|------------|
| 1 | B3 `validate_inputs` (cez B1, B2) | `RawInput` → `ValidationResult` | IN-01 až IN-06, FR-05, FR-09 |
| 2 | B4 `calculate_mortgage` | `LoanParams` → `LoanResult` (nezaokrúhlený) | FR-01 až FR-03, DR-01, DR-02 |
| 3 | B4 `balance_after(params, K)` | → B_K | DR-05 |
| 4 | B5 `round_down(B_K)` | → horná hranica IN-05 | IN-05 |
| 5 | B3 `validate_extra_against_loan` | K, E, n, hranica → chyby | FR-09 |
| 6 | B6 `calculate_extra` | `LoanParams`, `ExtraParams` → `ExtraResultRaw` | FR-06 až FR-08, DR-06 až DR-09 |
| 7 | B7, B8 | čísla → texty | FR-04, FR-06, FR-09 |
| 8 | B5 `round_half_up` | čísla → `SavedValues` | FR-10, AD-V2-08 |

Kroky 3 až 6 sa vykonajú iba vtedy, keď sú IN-04 aj IN-05 vyplnené. Pri chybe v kroku 1 alebo 5 B9 skončí a vráti `status: 'invalid'`.

Doplnenie dátového modelu z `02-architecture.md` (`SavedExtra` tam je použitý, ale nie je definovaný):

```python
@dataclass
class SavedExtra:                      # časť SavedValues, zaokrúhlené na 0,01 € (AD-V2-08)
    month: int; amount: Decimal; mode: Mode
    payments: int | None               # iba shorter_term (FR-06)
    last_payment: Decimal | None       # iba shorter_term (FR-06)
    new_monthly: Decimal | None        # iba lower_payment (FR-07)
    total_paid: Decimal; total_interest: Decimal; interest_saved: Decimal

@dataclass
class SavedRecord:                     # výstup B12/B13
    id: str; created_at: datetime      # UTC
    values: SavedValues
```

### 3.3 Endpointy (B11)

```python
# B11 – implementuje FR-10, FR-11, API-R5, API-R6
router = APIRouter(prefix='/api')

@router.post('/calculate', response_model=CalculationResponse)
def calculate(req: CalculationRequest) -> CalculationResponse: ...

@router.post('/calculations', status_code=201, response_model=SaveResponse,
             responses={422: {'model': InvalidResponse}, 503: {'model': StorageErrorBody}})
def save(req: CalculationRequest, repo: CalculationRepository = Depends(get_repository)): ...

@router.get('/calculations', response_model=CalculationList,
            responses={503: {'model': StorageErrorBody}})
def list_calculations(repo: CalculationRepository = Depends(get_repository)): ...

@router.get('/health')
def health() -> dict[str, str]: return {'status': 'ok'}
```

- Endpointy sú `def`, nie `async def`. Klient Supabase je synchrónny a FastAPI ich spustí v thread poole, takže neblokujú event loop.
- `StorageError` sa prevedie na 503 jedným `exception_handler` v B14, nie v každom endpointe.
- `save` volá `run_calculation` znova a ukladá `outcome.values` (AD-V2-12). Ak je `outcome.values is None`, vráti 422 s `InvalidResponse`.
- `list_calculations` prevedie `SavedRecord` na `SavedCalculation` cez B7, B7a a B8.

### 3.4 Prepojenie a nastavenia (B14, B15)

```python
# B14 – implementuje NFR-V2-08, AD-V2-05
app = FastAPI(title='Hypotekárna kalkulačka V2')
app.include_router(router)
app.add_exception_handler(StorageError, lambda req, exc: JSONResponse({'error': 'storage_unavailable'}, 503))
# testy: app.dependency_overrides[get_repository] = lambda: InMemoryRepository()
app.mount('/', StaticFiles(directory=FRONTEND_DIR, html=True), name='frontend')   # ako posledné
```

`StaticFiles` sa pripája ako posledné, inak by `/` prekrylo `/api`.

| Premenná (B15) | Povinná | Predvolené | Príklad |
|----------------|---------|------------|---------|
| `STORAGE` | nie | `supabase` | `memory` pre e2e |
| `SUPABASE_URL` | pri `STORAGE=supabase` | – | `https://<projekt>.supabase.co` |
| `SUPABASE_SERVICE_ROLE_KEY` | pri `STORAGE=supabase` | – | iba v `backend/.env` (NFR-V2-06) |

`backend/.env.example` (commituje sa):
```
STORAGE=supabase
SUPABASE_URL=
SUPABASE_SERVICE_ROLE_KEY=
```

### 3.5 Testy backendu

| Úroveň | Nástroj | Úložisko | Príklady |
|--------|---------|----------|----------|
| Jednotkové B1–B8 | `pytest` | – | `test_b5_round_half_up_1_005` (DR-03) |
| Akceptačné B9 | `pytest`, parametrizované | – | 4 riadky DR-04, 8 riadkov DR-10 |
| API B11 | `fastapi.testclient` | `InMemoryRepository` | 200/201/422/503 pre každý endpoint |
| Výkon | `TestClient`, 100 volaní | `InMemoryRepository` | medián ≤ 50 ms (NFR-V2-02) |
| Architektúra | `pytest` + `ast` | – | 0 zakázaných importov (NFR-V2-03) |
| B13 | ručný test | Supabase | 1 uloženie + 1 načítanie (AD-V2-09) |

503 sa testuje cez `InMemoryRepository(fail=True)`, ktorý vyhodí `StorageError`.

---

## 4. Supabase

### 4.1 Schéma

V2 má **1 tabuľku `calculations`**. Jeden riadok = jedno uloženie: vstupy IN-01 až IN-06 aj výsledky FR-01 až FR-08. História (FR-11) je `select … order by created_at desc limit 20` nad tou istou tabuľkou.

Prečo nie samostatné tabuľky pre vstupy, výsledky a históriu:

| Alternatíva | Prečo nie vo V2 |
|-------------|-----------------|
| `inputs` + `results` (1:1) | Každý zápis by potreboval 2 inserty v transakcii, každé čítanie join. Vzťah je vždy 1:1. |
| `user_history` | Používatelia neexistujú (OQ-V2-01, návrh: spoločný zoznam). Pridá sa pri EP-V2-03. |
| `calculation_extra_payments` | V2 má najviac 1 mimoriadnu splátku. Pridá sa pri EP-V2-01. |

SQL migrácia je v `supabase/migrations/20261015120000_create_calculations.sql` (S1). Zhoduje sa so SQL v `02-architecture.md`, časť Data Model → V Supabase.

### 4.2 Mapovanie stĺpcov

| Stĺpec | Typ | `SavedValues` (B9) | `SavedCalculation` (API) | Požiadavka |
|--------|-----|--------------------|--------------------------|------------|
| `id` | `uuid` | – (vytvorí DB) | `id` | FR-11 |
| `created_at` | `timestamptz` | – (vytvorí DB) | `createdAt` cez B7a | FR-11 |
| `amount` | `numeric(10,2)` | `amount` | `amount` cez B7 | IN-01 |
| `rate` | `numeric(4,2)` | `rate` | `rate` cez `format_rate` | IN-02 |
| `years` | `smallint` | `years` | `years` cez B8 | IN-03 |
| `monthly_payment` | `numeric(12,2)` | `monthly_payment` | `monthly` cez B7 | FR-01 |
| `total_paid` | `numeric(12,2)` | `total_paid` | – | FR-02 |
| `total_interest` | `numeric(12,2)` | `total_interest` | – | FR-03 |
| `extra_month` | `smallint` | `extra.month` | časť `extra` cez B8 | IN-04 |
| `extra_amount` | `numeric(10,2)` | `extra.amount` | časť `extra` cez B8 | IN-05 |
| `extra_mode` | `text` | `extra.mode` | časť `extra` cez B8 | IN-06 |
| `extra_payments` | `smallint` | `extra.payments` | – | FR-06 |
| `extra_last_payment` | `numeric(12,2)` | `extra.last_payment` | – | FR-06 |
| `extra_new_monthly` | `numeric(12,2)` | `extra.new_monthly` | – | FR-07 |
| `extra_total_paid` | `numeric(12,2)` | `extra.total_paid` | – | FR-06, FR-07 |
| `extra_total_interest` | `numeric(12,2)` | `extra.total_interest` | – | FR-06, FR-07 |
| `extra_interest_saved` | `numeric(12,2)` | `extra.interest_saved` | – | FR-08 |

- Ak `SavedValues.extra is None`, všetky stĺpce `extra_*` sú `NULL` (constraint `extra_all_or_nothing`).
- `Decimal` sa do JSON pre Supabase posiela ako text (`str(value)`), nie ako float, aby sa nestratili centy. PostgreSQL ho prevedie na `numeric`.
- Stĺpce bez API poľa sa ukladajú pre EP-V2-04 a pre kontrolu priamo v databáze.

### 4.3 Pripojenie (B13)

```python
# B13 – implementuje FR-10, FR-11, NFR-V2-06, NFR-V2-07
from supabase import create_client, ClientOptions

class SupabaseRepository:
    def __init__(self, url: str, key: str):
        self._client = create_client(url, key, options=ClientOptions(postgrest_client_timeout=4))

    def save(self, values: SavedValues) -> SavedRecord:
        # insert(to_row(values)).execute() → 1 riadok s id a created_at
        ...

    def list_latest(self, limit: int = 20) -> list[SavedRecord]:
        # select('*').order('created_at', desc=True).limit(limit).execute()
        ...
```

- Klient sa vytvorí 1× pri štarte aplikácie (B14), nie pri každej požiadavke.
- Každá výnimka klienta (sieť, timeout 4 s, chyba PostgREST) sa prevedie na `StorageError` (NFR-V2-07).
- Kľúč `service_role` obchádza RLS. Preto je iba v `backend/.env` a nikdy vo `frontend/` (AD-V2-06, NFR-V2-06).

### 4.4 Založenie projektu (jednorazovo)

| # | Krok | Overenie |
|---|------|----------|
| 1 | Na supabase.com vytvoriť projekt, región `eu-central-1` (Frankfurt). | Projekt má stav „Active“. |
| 2 | V SQL Editore spustiť `supabase/migrations/20261015120000_create_calculations.sql`. | V Table Editore je tabuľka `calculations` so 17 stĺpcami a značkou RLS enabled. |
| 3 | Settings → API: skopírovať Project URL a `service_role` kľúč do `backend/.env`. | `git status` neukazuje `.env` (NFR-V2-06). |
| 4 | Spustiť `uvicorn app.main:app` a uložiť 1 výpočet. | V tabuľke je 1 riadok s `monthly_payment = 477.42` (príklad FR-10). |
| 5 | Overiť, že anon kľúč nemá prístup: `GET <url>/rest/v1/calculations` s anon kľúčom. | Odpoveď je `[]` (RLS bez politík, AD-V2-06). |

Bezplatný projekt sa po 7 dňoch bez aktivity pozastaví (R-V2-03). Obnoví sa tlačidlom „Restore project“ v dashboarde.

### 4.5 Budúce rozšírenie o používateľov (EP-V2-03, nie je súčasťou V2)

Iba náčrt pre prípad, že OQ-V2-01 sa rozhodne pre prihlásenie:

```sql
-- 002_user_history.sql (NEPOUŽÍVA SA vo V2)
alter table public.calculations add column user_id uuid references auth.users (id);
create policy "vlastne zaznamy" on public.calculations
  for select using (user_id = auth.uid());
```

B12 by dostal `user_id` ako argument `save` a `list_latest`. B1–B9 sa nemenia.

---

## 5. Poradie implementácie podľa vrstiev

Presné kroky, verzie závislostí a commity určí `05-plan.md`. Odporúčané poradie, aby každá vrstva mala hotové to, od čoho závisí:

| # | Vrstva | Moduly | Hotové, keď |
|---|--------|--------|-------------|
| 1 | Backend jadro | B1–B9 | Prejde 12 akceptačných testov DR-04 a DR-10. |
| 2 | API | B10, B11, B12 (pamäťové), B14, B15 | `TestClient` prejde všetky príklady z časti 2.2. |
| 3 | Frontend | F1–F5 | Playwright so `STORAGE=memory` prejde FR-05 až FR-11. |
| 4 | Supabase | S1, B13 | Ručný test 4.4, kroky 4 a 5. |

## 6. Otvorené body z tohto dokumentu

| ID | Bod | Návrh |
|----|-----|-------|
| OQ-V2-04 | Text pre stav `unavailable` pri výpočte (1.4) chýba vo FR. | **Rozhodnuté (2026-10-15):** „Výpočet je dočasne nedostupný. Skúste to znova.“ s tlačidlom „Skúsiť znova“, výsledky sa skryjú. Doplniť do FR-05 V2 v review (04). |
| OQ-V2-05 | `SavedExtra` a `SavedRecord` (3.2) chýbajú v `02-architecture.md`. | Prevziať do Data Model v `02-architecture.md` v review (04). |
| OQ-V2-06 | Číslo `01` v názve tohto súboru sa prekrýva s `01-functional.md`. | Pri review (04) premenovať, napr. na `02a-tiers.md`, aby sedelo číselné poradie spracovania. |
