# 02 – Architektúra V2

## Stack

Aplikácia má 4 časti. Prehliadač iba zobrazuje, všetko ostatné robí server.

```
Používateľ ─► frontend/ (HTML + JS) ──JSON──► API (docs/v2/api-contract.md) ──► backend/ (FastAPI) ──► Supabase
                    ◄───────────── JSON s hotovými textmi ──────────────────────┘
```

| Časť | Voľba | Dôvod |
|------|-------|-------|
| Frontend | Čisté HTML + CSS + JavaScript (ES2022, natívne ES moduly), bez frameworku a bez build kroku | Má iba formulár, tlačidlo a dve oblasti s výsledkami. 0 závislostí za behu (NFR-V2-05). |
| API | REST + JSON, kontrakt v `docs/v2/api-contract.md` a v Pydantic modeloch (B10) | FastAPI z Pydantic modelov generuje OpenAPI, takže dokumentácia a kód sa kontrolujú navzájom. |
| Backend | Python ≥ 3.12, FastAPI, Uvicorn | Požiadavka zadania. `decimal` zo štandardnej knižnice vie zaokrúhliť polovicu nahor (AD-V2-10). |
| Databáza | Supabase (PostgreSQL), klient `supabase` pre Python | Požiadavka zadania. Prístup má iba backend (AD-V2-06). |
| Testy backendu | `pytest` a `fastapi.testclient` | Výpočet sa testuje bez siete a bez Supabase (AD-V2-09). |
| Testy frontendu | Playwright (`@playwright/test`), backend spustený s pamäťovým úložiskom | Frontend nemá logiku, testuje sa iba v prehliadači. |
| Spustenie | Z priečinka `backend/`: `uvicorn app.main:app` → `http://127.0.0.1:8000/` | Backend servíruje aj frontend, takže stačí jeden príkaz a nie je potrebné CORS (AD-V2-05). |

Závislosti backendu (`backend/requirements.txt`): `fastapi`, `uvicorn`, `supabase`, `python-dotenv`, `tzdata` (časové pásmo Europe/Bratislava na Windows). Vývojové závislosti (`backend/requirements-dev.txt`): `pytest`, `httpx`. Presné verzie určí `05-plan.md`.

Štruktúra projektu:

```
frontend/
  index.html                      F1 – markup formulára, výsledkov a zoznamu
  styles.css                      F2 – vzhľad
  js/main.js                      F3 – vstupný bod: debounce a prepojenie F4 a F5
  js/view.js                      F4 – DOM adaptér: čítanie formulára a vykreslenie
  js/api.js                       F5 – jediné miesto s volaním fetch()

backend/
  app/main.py                     B14 – vytvorenie aplikácie FastAPI, prepojenie, servírovanie frontend/
  app/config.py                   B15 – načítanie nastavení z .env
  app/input/parse.py              B1  – prevod textu na číslo                      (V1: M1)
  app/input/limits.py             B2  – hranice vstupov                             (V1: M2)
  app/input/validate.py           B3  – validácia vstupov                           (V1: M3)
  app/domain/mortgage.py          B4  – splátka, súčty, zostatok                    (V1: M4)
  app/domain/rounding.py          B5  – zaokrúhľovanie                              (V1: M5)
  app/domain/extra_payment.py     B6  – mimoriadna splátka                          NOVÉ
  app/format/money.py             B7  – formát súm, čísel a sadzby                  (V1: M6)
  app/format/datetime.py          B7a – formát dátumu a času                        NOVÉ
  app/text/messages.py            B8  – chybové správy a tvary slov                 (V1: M7)
  app/services/calculator.py      B9  – riadi jeden výpočet                         (V1: M8)
  app/api/schemas.py              B10 – API kontrakt v kóde                         NOVÉ
  app/api/routes.py               B11 – endpointy                                   NOVÉ
  app/db/repository.py            B12 – rozhranie úložiska a pamäťová implementácia NOVÉ
  app/db/supabase_repository.py   B13 – implementácia úložiska nad Supabase         NOVÉ
  db/migrations/001_calculations.sql  S1 – tabuľka a RLS v Supabase                 NOVÉ
  tests/                          zrkadlí app/; každý test uvádza ID požiadavky
  requirements.txt, requirements-dev.txt
  .env.example                    názvy premenných bez hodnôt (NFR-V2-06)

e2e/                              testy Playwright (F1 až F5 cez prehliadač)
docs/
  v1/                             bez zmeny, história
  v2/                             tento plán
```

## Čo sa presúva z V1

| V1 | V2 | Zmena |
|----|----|-------|
| M1 až M8 (`src/input`, `src/domain`, `src/format`, `src/text`, `src/app`) | B1 až B9 v `backend/app/` | Prepis z JavaScriptu do Pythonu. Pravidlá, rozhrania a invarianty zostávajú. Rozšírenie o IN-04 až IN-06 a FR-06 až FR-11. |
| M9 `src/ui/view.js` | F4 `frontend/js/view.js` | Pribudnú polia mimoriadnej splátky, tlačidlo „Uložiť výpočet“ a zoznam uložených výpočtov. |
| M10 `src/main.js` | F3 `frontend/js/main.js` | Namiesto volania M8 volá F5 (API) s debounce 300 ms. |
| M11 `index.html`, M12 `styles.css` | F1, F2 vo `frontend/` | Nové polia a zoznam. |
| Dátový model z 02 V1 (`RawInput`, `CalculationResult`) | B10 a `api-contract.md` | Z interných typov sa stáva verejný kontrakt. |
| EP-03 (mimoriadne splátky), EP-08 (ukladanie) | B6, B12, B13, S1 | Body rozšírenia z V1 sa realizujú. EP-08 ukladá do databázy namiesto URL. |

## Modules

Každý modul má jednu zodpovednosť (jeden dôvod na zmenu), rovnako ako vo V1 (AD-09 V1).
Pri moduloch prevzatých z V1 sa uvádza iba rozdiel. Ostatné platí podľa `docs/v1/02-architecture.md`.

### Backend – výpočet (bez FastAPI a bez databázy, NFR-V2-03)

#### B1 `app/input/parse.py` – prevod textu na číslo (V1: M1)
- **Jednou vetou:** Prevedie surový text na číslo podľa pravidiel zápisu z časti 3 `docs/v1/01-functional.md`.
- **Rozdiel oproti M1:** výsledok je `Decimal`, nie float. Počet desatinných miest sa tak zistí presne a validácia nemusí pracovať s chybami binárnej aritmetiky.
- **Rozhranie:** `parse_number(raw: str) -> ParsedNumber`
- **Implementuje:** IN-01 až IN-05 (zápis čísla), FR-05, FR-09 (podmienky „je prázdny“ a „nie je číslo“).

#### B2 `app/input/limits.py` – hranice vstupov (V1: M2)
- **Jednou vetou:** Uchováva statické hranice každého vstupu.
- **Rozdiel oproti M2:** pribudnú `extra_month: {min: 1, max: 359, decimals: 0}` a `extra_amount: {min: 100, max: 1 000 000, decimals: 2}`. Hranice závislé od úveru (n − 1, zostatok B_K) tu nie sú, počíta ich B9 (pozri B3).
- **Implementuje:** IN-01 až IN-05 (hodnoty hraníc).

#### B3 `app/input/validate.py` – validácia vstupov (V1: M3)
- **Jednou vetou:** Rozhodne o platnosti vstupov podľa hraníc, ktoré dostane.
- **Zodpovednosť:**
  - `validate_inputs` overí všetkých 5 polí naraz so statickými hranicami z B2, v poradí z M3: prázdne → nie je číslo → priveľa desatinných miest → mimo rozsahu. Pravidlo „IN-04 a IN-05 obe prázdne = bez mimoriadnej splátky“ je tu.
  - `validate_extra_against_loan` overí hranice závislé od úveru: K ≤ n − 1 a E < zostatok zaokrúhlený nadol. Hodnotu zostatku dostane ako argument, aby B3 neimportoval doménu.
  - Nevytvára texty správ.
- **Rozhranie:**
  ```python
  validate_inputs(raw: RawInput) -> ValidationResult
  validate_extra_against_loan(month: int, amount: Decimal, n: int, balance_floor: Decimal) -> dict[FieldKey, ErrorCode]
  ```
- **Implementuje:** IN-01 až IN-06, FR-05, FR-09 (zistenie neplatného vstupu).

#### B4 `app/domain/mortgage.py` – výpočet (V1: M4)
- **Jednou vetou:** Vypočíta nezaokrúhlenú splátku, súčty a zostatok úveru.
- **Rozdiel oproti M4:** pribudne `balance_after(params, months)` podľa DR-05, ktorú používajú B6 a B9. Vzorec splátky sa nemení.
- **Rozhranie:**
  ```python
  calculate_mortgage(params: LoanParams) -> LoanResult
  annuity_payment(principal: float, monthly_rate: float, n: int) -> float   # DR-01, DR-02
  balance_after(params: LoanParams, months: int) -> float                   # DR-05
  ```
- **Implementuje:** FR-01 až FR-03, DR-01 až DR-03, DR-05.

#### B5 `app/domain/rounding.py` – zaokrúhľovanie (V1: M5)
- **Jednou vetou:** Zaokrúhli číslo na zadaný počet desatinných miest podľa DR-03.
- **Rozdiel oproti M5:**
  - Zaokrúhľuje sa cez `Decimal(repr(value)).quantize(..., ROUND_HALF_UP)`. Python `round()` zaokrúhľuje na párne číslo (`round(0.125, 2) == 0.12`), preto sa nepoužíva (AD-V2-10).
  - Pravidlo |value| < 1e-6 → 0 a „nikdy nie −0“ platí ďalej.
  - Pribudne `round_down` pre hornú hranicu IN-05.
- **Rozhranie:**
  ```python
  round_half_up(value: float, decimals: int = 2) -> Decimal
  round_down(value: float, decimals: int = 2) -> Decimal
  ```
- **Implementuje:** DR-03, IN-05 (hranica zaokrúhlená nadol).

#### B6 `app/domain/extra_payment.py` – mimoriadna splátka (NOVÉ)
- **Jednou vetou:** Vypočíta nezaokrúhlený priebeh úveru po jednej mimoriadnej splátke.
- **Zodpovednosť:**
  - Z B'_K (DR-06) vypočíta režim „Kratšia doba“ (DR-07) alebo „Nižšia splátka“ (DR-08) a súčty podľa DR-09.
  - Pri DR-07 sa zostatok ≤ 1e-6 € považuje za 0, rovnako ako v B5.
  - Používa iba B4. Nezaokrúhľuje a nevaliduje.
- **Dôvod zmeny:** zmena pravidiel mimoriadnej splátky.
- **Rozhranie:**
  ```python
  calculate_extra(params: LoanParams, extra: ExtraParams) -> ExtraResultRaw
  ```
- **Implementuje:** FR-06, FR-07, FR-08, DR-05 až DR-09.

#### B7 `app/format/money.py` – formát čísel (V1: M6)
- **Jednou vetou:** Prevedie číslo na text v slovenskom formáte.
- **Rozdiel oproti M6:** pribudne `format_rate` (`4` → `"4,00 %"`, FR-11). Formátuje sa ručne, nie cez `locale` (rovnaký dôvod ako AD-04 V1: výstup musí mať obyčajnú medzeru).
- **Rozhranie:** `format_money(v) -> str`, `format_number(v, decimals) -> str`, `format_rate(v) -> str`
- **Implementuje:** FR-04, FR-11 (sadzba), DR-03.

#### B7a `app/format/datetime.py` – formát dátumu (NOVÉ)
- **Jednou vetou:** Prevedie čas uloženia v UTC na text `15. 10. 2026 14:05` v pásme Europe/Bratislava.
- **Dôvod zmeny:** zmena formátu dátumu alebo časového pásma.
- **Rozhranie:** `format_datetime(utc: datetime) -> str`
- **Implementuje:** FR-11 (dátum a čas).

#### B8 `app/text/messages.py` – texty (V1: M7)
- **Jednou vetou:** Vytvorí slovenské texty pre používateľa.
- **Rozdiel oproti M7:**
  - Pribudnú správy FR-09 (s hodnotou n − 1, zostatkom alebo mesiacom K), správy FR-10 a FR-11 a tvary slov podľa čísla (mesiac/mesiace/mesiacov, rok/roky/rokov).
  - Pribudnú texty výsledkov `"300 mesiacov (o 60 mesiacov menej)"` a `"10 000,00 € v 12. mesiaci, kratšia doba"`.
- **Implementuje:** FR-05, FR-06 (text počtu splátok), FR-09, FR-10, FR-11 (texty).

#### B9 `app/services/calculator.py` – orchestrácia (V1: M8)
- **Jednou vetou:** Riadi poradie krokov jedného výpočtu od surových textov po `CalculationResponse`.
- **Zodpovednosť:**
  - Kroky: B3 statická validácia → B4 → (ak je mimoriadna splátka) B4 `balance_after` → B5 `round_down` → B3 `validate_extra_against_loan` → B6 → B7 a B8.
  - Pri ľubovoľnej chybe vráti iba chyby, žiadne výsledky (FR-05, FR-09).
  - Vracia aj zaokrúhlené čísla na uloženie (`SavedValues`) pre B11. Do API odpovede idú iba texty.
  - Sám nič nepočíta, neformátuje ani nevaliduje.
- **Rozhranie:**
  ```python
  run_calculation(raw: RawInput) -> CalculationOutcome   # .response: CalculationResponse, .values: SavedValues | None
  ```
- **Implementuje:** FR-01 až FR-09 (end-to-end), DR-04, DR-10 (akceptačné testy).

### Backend – API a úložisko

#### B10 `app/api/schemas.py` – API kontrakt (NOVÉ)
- **Jednou vetou:** Definuje Pydantic modely všetkých požiadaviek a odpovedí podľa `api-contract.md`.
- **Zodpovednosť:** typy `CalculationRequest`, `CalculationResponse`, `SavedCalculation` a ďalšie. Kľúče sú `camelCase` cez alias (API-R2). `mode` je `Literal['shorter_term', 'lower_payment']`, takže iná hodnota vráti 422 (API-R6).
- **Dôvod zmeny:** zmena kontraktu. Každá zmena B10 musí byť aj v `api-contract.md`.
- **Implementuje:** API-R1 až API-R6.

#### B11 `app/api/routes.py` – endpointy (NOVÉ)
- **Jednou vetou:** Prekladá HTTP požiadavky na volania B9 a B12 a ich výsledky na HTTP odpovede.
- **Zodpovednosť:** 4 endpointy z `api-contract.md`. Výnimku úložiska (`StorageError`) prevedie na 503. Úložisko dostane cez `Depends`, nevytvára ho.
- **Dôvod zmeny:** zmena endpointov alebo HTTP kódov.
- **Implementuje:** FR-10, FR-11 (serverová časť), API-R5, API-R6.

#### B12 `app/db/repository.py` – rozhranie úložiska (NOVÉ)
- **Jednou vetou:** Definuje, čo úložisko výpočtov vie, a obsahuje jeho pamäťovú implementáciu pre testy.
- **Rozhranie:**
  ```python
  class CalculationRepository(Protocol):
      def save(self, values: SavedValues) -> SavedRecord: ...        # vyhodí StorageError
      def list_latest(self, limit: int = 20) -> list[SavedRecord]: ...
  class InMemoryRepository: ...                                     # testy a e2e
  ```
- **Dôvod zmeny:** zmena toho, čo sa o výpočte ukladá.
- **Implementuje:** FR-10, FR-11 (bez závislosti na Supabase, AD-V2-09).

#### B13 `app/db/supabase_repository.py` – Supabase (NOVÉ)
- **Jednou vetou:** Implementuje `CalculationRepository` nad tabuľkou `calculations` v Supabase.
- **Zodpovednosť:** prevod `SavedValues` na riadok tabuľky a späť. Každú chybu klienta Supabase alebo prekročenie času 4 s prevedie na `StorageError`.
- **Dôvod zmeny:** zmena databázy alebo jej klienta.
- **Implementuje:** FR-10, FR-11, NFR-V2-06, NFR-V2-07.

#### B14 `app/main.py` – vstupný bod (NOVÉ)
- **Jednou vetou:** Vytvorí aplikáciu FastAPI a prepojí routy, úložisko a statické súbory.
- **Zodpovednosť:** pripojí B11 pod `/api`, pripojí `frontend/` cez `StaticFiles` na `/` a podľa B15 zvolí B13. Ak premenná `STORAGE=memory`, zvolí `InMemoryRepository` (pre e2e testy).
- **Implementuje:** NFR-V2-08, AD-V2-05.

#### B15 `app/config.py` – nastavenia (NOVÉ)
- **Jednou vetou:** Načíta nastavenia z premenných prostredia a súboru `backend/.env`.
- **Rozhranie:** `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, `STORAGE` (`supabase` | `memory`, predvolene `supabase`). Ak pri `STORAGE=supabase` chýba URL alebo kľúč, aplikácia sa nespustí a vypíše názov chýbajúcej premennej.
- **Implementuje:** NFR-V2-06.

#### S1 `db/migrations/001_calculations.sql` – tabuľka (NOVÉ)
- **Jednou vetou:** Vytvorí v Supabase tabuľku `calculations` a zapne RLS.
- **Spustenie:** ručne v Supabase SQL Editore, raz. Postup bude v README.
- **Implementuje:** FR-10, FR-11, AD-V2-06.

### Frontend (bez výpočtu, NFR-V2-05)

#### F1 `index.html` – markup (V1: M11)
- **Rozdiel oproti M11:** pribudne `<fieldset>` „Mimoriadna splátka“ s poliami IN-04, IN-05 (`type="text"`, AD-03 V1), prepínačom IN-06 (2× `<input type="radio">`, predvolene „Kratšia doba“), oblasť výsledkov FR-06/FR-07, tlačidlo „Uložiť výpočet“, oblasť správy FR-10 (`role="status"`) a tabuľka FR-11.
- **Implementuje:** NFR-V2-04.

#### F2 `styles.css` – vzhľad (V1: M12)
- **Rozdiel oproti M12:** štýly nových oblastí. Sumy sa nezalomia (FR-04).

#### F3 `js/main.js` – vstupný bod (V1: M10)
- **Jednou vetou:** Prepojí F4 a F5 a riadi, kedy sa volá API.
- **Zodpovednosť:**
  - Pri udalosti `input` počká 300 ms bez ďalšej zmeny a potom zavolá `POST /api/calculate` (AD-V2-02).
  - Zobrazí iba odpoveď na poslednú odoslanú požiadavku. Staršie odpovede zahodí, lebo môžu prísť neskôr ako novšie.
  - Pri načítaní stránky zavolá výpočet s predvyplnenými hodnotami (AD-08 V1) a `GET /api/calculations`.
  - Pri kliknutí na „Uložiť výpočet“ zavolá `POST /api/calculations` a po úspechu znova načíta zoznam.
- **Implementuje:** FR-10, FR-11 (priebeh), NFR-V2-01.

#### F4 `js/view.js` – DOM adaptér (V1: M9)
- **Jednou vetou:** Synchronizuje stránku HTML s objektmi z API kontraktu.
- **Rozdiel oproti M9:** číta aj IN-04 až IN-06, vykreslí `results.extra`, zoznam `SavedCalculation[]`, správy FR-10/FR-11 a zapína a vypína tlačidlo „Uložiť výpočet“ podľa `status`. Chyby priradí k poliam podľa `FieldKey`. Nič nepočíta ani neformátuje (API-R4).
- **Implementuje:** FR-05, FR-09 (zobrazenie), FR-10, FR-11 (zobrazenie), NFR-V2-04.

#### F5 `js/api.js` – klient API (NOVÉ)
- **Jednou vetou:** Posiela požiadavky na API a vracia odpoveď alebo typ chyby.
- **Zodpovednosť:** jediné miesto s `fetch()`. Čaká najviac 5 s (`AbortController`, API-R7). Chybu siete, prekročenie času a 503 vráti ako `{ error: 'network' | 'timeout' | 'storage' }` a nevyhodí výnimku.
- **Rozhranie:**
  ```js
  calculate(req: CalculationRequest) → Promise<CalculationResponse | ApiError>
  saveCalculation(req: CalculationRequest) → Promise<{ id, createdAt } | ApiError>
  listCalculations() → Promise<{ items: SavedCalculation[] } | ApiError>
  ```
- **Dôvod zmeny:** zmena URL, HTTP kódov alebo časového limitu.
- **Implementuje:** API-R1, API-R7.

### Overenie SRP

| Modul | Jedna zodpovednosť? | Poznámka |
|-------|---------------------|----------|
| B1–B5, B7–B9 | Áno | Rovnaké hranice ako M1 až M8 vo V1. |
| B3 | Áno | Dve funkcie, ale jeden dôvod zmeny: pravidlá platnosti. Zostatok dostane ako argument, takže nezávisí od domény. |
| B5 | Áno | `round_down` je pravidlo zaokrúhlenia, rovnaký dôvod zmeny ako `round_half_up`. |
| B6 | Áno | Iba mimoriadna splátka. Vzorec anuity sa nekopíruje, berie sa z B4. |
| B7 / B7a | Áno | **Rozdelené:** formát dátumu sa mení z iného dôvodu (časové pásmo) ako formát sumy. |
| B10 / B11 | Áno | **Rozdelené:** tvar dát (kontrakt) sa mení inak ako HTTP správanie (kódy, závislosti). |
| B12 / B13 | Áno | **Rozdelené:** čo sa ukladá (B12) a kam sa ukladá (B13). Testy tak nepotrebujú Supabase. |
| B14 / B15 | Áno | Prepojenie vs. čítanie nastavení. |
| F3 / F4 / F5 | Áno | Kedy volať (F3), čo je v DOM (F4) a ako volať HTTP (F5). |

### Matica sledovateľnosti

| Požiadavka | Moduly |
|------------|--------|
| FR-01 až FR-03 | B4, B9, F4 |
| FR-04 | B5, B7, F2 |
| FR-05 | B1, B3, B8, B9, F4 |
| FR-06, FR-07 | B4, B6, B8, B9, F4 |
| FR-08 | B6, B9 |
| FR-09 | B1, B2, B3, B5, B8, B9, F4 |
| FR-10 | B9, B11, B12, B13, S1, F3, F4, F5 |
| FR-11 | B7, B7a, B8, B11, B12, B13, S1, F3, F4, F5 |
| IN-01 až IN-03 | B1, B2, B3 |
| IN-04 až IN-06 | B1, B2, B3, B5, B10, F1 |
| DR-01 až DR-03 | B4, B5, B7 |
| DR-04, DR-10 | B9 (akceptačné testy) |
| DR-05 až DR-09 | B4, B6 |
| API-R1 až API-R7 | B10, B11, F5 |
| NFR-V2-01 až NFR-V2-08 | pozri tabuľku NFR |

## Dependency Direction

```
F3 main.js ──► F4 view.js
     └──────► F5 api.js ──HTTP──► B11 routes.py ──► B10 schemas.py
                                       ├──────────► B9 calculator.py ──► B3 ──► B1, B2
                                       │                              ├─► B4 ◄── B6
                                       │                              ├─► B6
                                       │                              ├─► B5
                                       │                              ├─► B7 ──► B5
                                       │                              └─► B8 ──► B2, B7
                                       └──────────► B12 repository.py (Protocol) ◄── B13 ──► Supabase (S1)
B14 main.py ──► B11, B12, B13, B15, frontend/ (StaticFiles)
B11 ──► B7a (formát dátumu v zozname)
```

Pravidlá:
1. B1 až B9 neimportujú `fastapi`, `supabase`, `pydantic` ani `app.api` a `app.db` (NFR-V2-03).
2. B4, B5 a B1 neimportujú žiadny modul aplikácie. B6 importuje iba B4.
3. B11 nevytvára úložisko, dostane ho cez `Depends` (AD-V2-09).
4. Iba B13 importuje `supabase`. Iba B15 číta premenné prostredia.
5. Frontend importuje iba súbory z `frontend/js/`. Iba F5 volá `fetch()`. Iba F4 používa `document`.
6. Cyklické závislosti nie sú povolené.
7. Pravidlá 1, 2, 4 a 5 overí test, ktorý prehľadá importy v `backend/app/` a výskyty `fetch(` a `document` vo `frontend/js/`.

## Data Model

### V backende

```python
FieldKey = Literal['amount', 'rate', 'years', 'extraMonth', 'extraAmount']
Mode = Literal['shorter_term', 'lower_payment']

@dataclass
class RawInput:                       # surové texty z CalculationRequest
    amount: str; rate: str; years: str
    extra_month: str; extra_amount: str; mode: Mode

@dataclass
class LoanParams:                     # ako V1
    principal: float; annual_rate_pct: float; years: int

@dataclass
class ExtraParams:
    month: int; amount: float; mode: Mode

@dataclass
class ExtraResultRaw:                 # výstup B6, nezaokrúhlený (DR-03)
    total_paid: float; total_interest: float; interest_saved: float
    payments: int | None              # iba shorter_term
    last_payment: float | None        # iba shorter_term
    new_monthly: float | None         # iba lower_payment

@dataclass
class SavedValues:                    # výstup B9 pre B12, zaokrúhlené na 0,01 € (AD-V2-08)
    amount: Decimal; rate: Decimal; years: int
    monthly_payment: Decimal; total_paid: Decimal; total_interest: Decimal
    extra: SavedExtra | None
```

Tok dát:

```
udalosť input → (300 ms) → F4.readForm → F5.calculate → POST /api/calculate
  → B10 CalculationRequest → B11 → B9.run_calculation(RawInput)
      → B3.validate_inputs → invalid → B8 → { status: 'invalid' }
      → B4.calculate_mortgage
      → mimoriadna splátka: B4.balance_after → B5.round_down → B3.validate_extra_against_loan
                            → invalid → B8 → { status: 'invalid' }
                            → B6.calculate_extra
      → B7, B8 → { status: 'ok', results }
  → F4.render

klik „Uložiť výpočet“ → F5.saveCalculation → POST /api/calculations
  → B11 → B9 (výpočet znova) → B12/B13.save(SavedValues) → 201 → F3 → F5.listCalculations → F4.renderList
```

### V Supabase (S1)

```sql
create table public.calculations (
  id                   uuid primary key default gen_random_uuid(),
  created_at           timestamptz not null default now(),
  amount               numeric(10,2) not null check (amount between 1000 and 1000000),   -- IN-01
  rate                 numeric(4,2)  not null check (rate between 0 and 20),             -- IN-02
  years                smallint      not null check (years between 1 and 30),            -- IN-03
  monthly_payment      numeric(12,2) not null,                                           -- FR-01
  total_paid           numeric(12,2) not null,                                           -- FR-02
  total_interest       numeric(12,2) not null,                                           -- FR-03
  extra_month          smallint      check (extra_month between 1 and 359),              -- IN-04
  extra_amount         numeric(10,2) check (extra_amount >= 100),                        -- IN-05
  extra_mode           text          check (extra_mode in ('shorter_term', 'lower_payment')), -- IN-06
  extra_payments       smallint,                                                         -- FR-06
  extra_last_payment   numeric(12,2),                                                    -- FR-06
  extra_new_monthly    numeric(12,2),                                                    -- FR-07
  extra_total_paid     numeric(12,2),                                                    -- FR-06, FR-07
  extra_total_interest numeric(12,2),                                                    -- FR-06, FR-07
  extra_interest_saved numeric(12,2),                                                    -- FR-08
  constraint extra_all_or_nothing check (
    (extra_month is null) = (extra_amount is null) and
    (extra_month is null) = (extra_mode is null) and
    (extra_month is null) = (extra_total_paid is null))
);
create index calculations_created_at_idx on public.calculations (created_at desc);
alter table public.calculations enable row level security;   -- bez politík: anon kľúč nemá prístup (AD-V2-06)
```

Najväčšia suma v tabuľke je 6 015 667,27 € (DR-04), `numeric(12,2)` dovoľuje až 9 999 999 999,99.

Invarianty:
- Text sa na číslo prevádza iba v B1. Vo frontende sa neprevádza vôbec.
- Zaokrúhľuje sa iba v B5 (cez B7 alebo pri `SavedValues`). `LoanResult` a `ExtraResultRaw` sú vždy nezaokrúhlené (DR-03).
- `status: 'invalid'` nikdy neobsahuje výsledky a `status: 'ok'` nikdy neobsahuje chyby (FR-05, FR-09).
- Do databázy sa zapisuje iba cez `POST /api/calculations`, nikdy pri `POST /api/calculate` (AD-V2-07).
- Uložený záznam sa už neprepočítava. Ak sa neskôr zmení vzorec, staré záznamy zostanú také, ako boli zobrazené (AD-V2-08).

## Extension Points & Decisions

### Body rozšírenia

| # | Funkcia (01, časť 6) | Bod rozšírenia | Čo sa nemení |
|---|----------------------|----------------|--------------|
| EP-V2-01 | Viac mimoriadnych splátok | `ExtraParams` sa zmení na zoznam. B6 ich spracuje postupne v jednom prechode zostatkom (DR-05). V Supabase pribudne tabuľka `calculation_extra_payments` s cudzím kľúčom. | B1, B4, B5, B7 |
| EP-V2-02 | Splátkový kalendár | B6 už prechádza zostatok po mesiacoch. Riadky vráti ako zoznam, B10 pridá `schedule`, F4 vykreslí tabuľku. | B1–B5 |
| EP-V2-03 | Prihlásenie (OQ-V2-01) | Supabase Auth. Stĺpec `user_id` v S1, RLS politika `user_id = auth.uid()`, B12 dostane `user_id`. | B1–B9 |
| EP-V2-04 | Otvorenie uloženého výpočtu | `GET /api/calculations/{id}` vráti `CalculationRequest`. Na to treba uložiť aj surové texty, nie iba čísla. | B1–B9 |
| EP-V2-05 | Nasadenie na internet | B14 a B15 dostanú zoznam povolených pôvodov (CORS), ak frontend pobeží inde. | Celý výpočet |

### Nefunkčné požiadavky

Nahrádzajú NFR-01 až NFR-03 z V1. NFR-04 V1 platí ďalej ako súčasť NFR-V2-04.

| ID | Požiadavka |
|----|------------|
| NFR-V2-01 | Frontend odošle `POST /api/calculate` 300 ms po poslednej zmene vstupu. Výsledok sa zobrazí najneskôr 500 ms po poslednej zmene, ak backend beží na tom istom počítači. |
| NFR-V2-02 | Backend spracuje `POST /api/calculate` v čase ≤ 50 ms (medián zo 100 volaní cez `TestClient`, s mimoriadnou splátkou v mesiaci 1 pri 30 rokoch). |
| NFR-V2-03 | B1 až B9 obsahujú 0 importov `fastapi`, `pydantic`, `supabase`, `app.api` a `app.db`. |
| NFR-V2-04 | Každý vstup má `<label>`, prepínač IN-06 je v `<fieldset>` s `<legend>`. Neplatný vstup má `aria-invalid="true"` a `aria-describedby` na správu (NFR-04 V1). Správy FR-10 sú v oblasti `role="status"`. |
| NFR-V2-05 | Frontend má 0 závislostí za behu (0 balíkov z npm, 0 načítaní z CDN). Obsahuje 0 hraníc vstupov, 0 vzorcov a 0 formátovania čísel. Všetko prichádza z API (API-R4). |
| NFR-V2-06 | Kľúč Supabase je iba v `backend/.env`. `.env` je v `.gitignore`. V gite a vo `frontend/` je 0 výskytov hodnoty kľúča. Do repozitára ide iba `backend/.env.example` s názvami premenných. |
| NFR-V2-07 | Uloženie (FR-10) a načítanie zoznamu (FR-11) trvajú ≤ 2 s. B13 čaká na Supabase najviac 4 s a potom vráti `StorageError`. |
| NFR-V2-08 | Aplikácia sa spustí jedným príkazom z `backend/` (`uvicorn app.main:app`) na `http://127.0.0.1:8000/`. Python ≥ 3.12. |

### Rozhodnutia

| # | Rozhodnutie | Dôvod / kompromis |
|---|-------------|-------------------|
| AD-V2-01 | Parsovanie, validácia, výpočet, formát aj texty sú v backende. Frontend posiela surové texty a zobrazuje hotové texty. | Pravidlá sú na jednom mieste a nemôžu sa rozísť medzi JS a Pythonom. Kompromis: aj chyba „prázdne pole“ potrebuje volanie API. |
| AD-V2-02 | **Nahrádza AD-01 V1:** výpočet sa volá 300 ms po poslednej zmene vstupu (debounce), nie pri každom znaku. | Pri písaní `150000` vznikne 1 požiadavka namiesto 6. Kompromis: výsledok sa zobrazí o 300 ms neskôr ako vo V1 (NFR-V2-01). |
| AD-V2-03 | Neplatný vstup = HTTP 200 so `status: 'invalid'`. HTTP 422 iba pri porušení kontraktu. | Počas písania je neplatný vstup bežný stav, nie chyba. Tvar odpovede zostáva rovnaký ako `CalculationResult` vo V1. |
| AD-V2-04 | Jeden endpoint `POST /api/calculate` pre základný výpočet aj mimoriadnu splátku (namiesto dvoch endpointov z prvého návrhu). | Mimoriadna splátka potrebuje tie isté IN-01 až IN-03. Pri dvoch endpointoch by frontend posielal vstupy dvakrát a musel by spájať chyby z dvoch odpovedí, čo je logika vo frontende. |
| AD-V2-05 | Backend servíruje `frontend/` cez `StaticFiles`. | Frontend aj API majú rovnaký pôvod, takže netreba CORS a stačí jeden príkaz na spustenie. Kompromis: frontend sa nedá nasadiť samostatne bez EP-V2-05. |
| AD-V2-06 | K Supabase pristupuje iba backend kľúčom `service_role`. RLS je zapnuté bez politík. | Kľúč nikdy nie je v prehliadači. Ani anon kľúč nemá prístup k tabuľke. |
| AD-V2-07 | Ukladá sa iba po kliknutí na „Uložiť výpočet“. | Pri automatickom ukladaní by vznikol záznam pri každom prepočte, aj s polovične napísanými hodnotami. |
| AD-V2-08 | Ukladajú sa platné vstupy ako čísla a výsledky zaokrúhlené na 0,01 €. Pri čítaní sa neprepočítavajú. | Záznam ukazuje to, čo videl používateľ. Kompromis: surové texty sa neukladajú (pozri EP-V2-04). |
| AD-V2-09 | Úložisko je za rozhraním `CalculationRepository`. Testy a e2e používajú `InMemoryRepository`. | Testy nepotrebujú internet ani účet Supabase. Kompromis: B13 sa overí iba ručným testom proti skutočnej databáze. |
| AD-V2-10 | Zaokrúhľuje sa cez `Decimal(repr(x))` a `ROUND_HALF_UP`. | `repr` dáva najkratší zápis floatu rovnako ako JavaScript v V1, takže `1.005` → `1.01`. `round()` v Pythone zaokrúhľuje na párne číslo. |
| AD-V2-11 | Zostatok sa počas splácania nezaokrúhľuje (DR-03 platí aj pre DR-05). | Rovnaké pravidlo ako vo V1. Kompromis: výsledky sa môžu od banky líšiť o niekoľko centov (poznámka v časti 5 `01-functional.md`). |
| AD-V2-12 | Backend overí výpočet znova aj pri ukladaní a neverí výsledkom z frontendu. | Do databázy sa nedostane výsledok, ktorý backend nevypočítal. |

### Riziká

| # | Riziko | Opatrenie |
|---|--------|-----------|
| R-V2-01 | Python nie je na počítači nainštalovaný (R-01 V1). | Nainštalovať Python ≥ 3.12 pred krokom 1 plánu V2. Overiť príkazom `python --version`. |
| R-V2-02 | Výsledky Pythonu sa líšia od V1 v JavaScripte (iná aritmetika alebo zaokrúhlenie). | Akceptačné testy B9 na všetkých 4 riadkoch DR-04 a 8 riadkoch DR-10. Test B5 s hodnotami `1.005`, `0.125` a `-1.8e-12`. |
| R-V2-03 | Bezplatný projekt Supabase sa po 7 dňoch bez aktivity pozastaví. | FR-11 má správu pri chybe a kalkulačka funguje ďalej. Postup obnovenia projektu bude v README. |
| R-V2-04 | Odpovede na `POST /api/calculate` prídu v inom poradí, ako boli odoslané. | F3 zobrazí iba odpoveď na poslednú požiadavku (test e2e so spomaleným backendom). |
| R-V2-05 | Kľúč Supabase sa omylom commitne. | `.gitignore` od kroku 1, `.env.example` bez hodnôt, test NFR-V2-06 prehľadá repozitár. |

### Kontrola pred ďalšou vrstvou

| # | Kontrola | Výsledok | Dôkaz |
|---|----------|----------|-------|
| K-01 | Každú požiadavku z `01-functional.md` V2 implementuje aspoň jeden modul. | Splnené | Matica sledovateľnosti pokrýva FR-01 až FR-11, IN-01 až IN-06 a DR-01 až DR-10. |
| K-02 | Každý modul sa dá opísať jednou vetou. | Splnené (22/22) | Riadky „Jednou vetou“, pri prevzatých moduloch platí veta z V1. |
| K-03 | Výpočet nezávisí od UI, API ani databázy. | Splnené | Pravidlo 1 v Dependency Direction a NFR-V2-03. Overí ho test importov (pravidlo 7). |
| K-04 | Kľúč k databáze nie je vo frontende. | Splnené | AD-V2-06, NFR-V2-06, pravidlo 4 v Dependency Direction. |
| K-05 | Otvorené otázky sú zapísané. | Splnené | OQ-V2-01 až OQ-V2-03 v `01-functional.md`. |
