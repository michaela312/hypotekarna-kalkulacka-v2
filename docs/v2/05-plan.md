# 05 – Implementačný plán V2 (4 vrstvy)

Tento plán dokončuje prechod kalkulačky na 4 vrstvy s jednou zodpovednosťou:

| Vrstva | Zodpovednosť | Čo **nerobí** | Kde |
|--------|--------------|---------------|-----|
| 1. Frontend (JavaScript) | Číta vstupy z formulára, volá API, zobrazuje hotové texty. | Neparsuje, nevaliduje, nepočíta, neformátuje čísla (NFR-V2-05). | `frontend/index.html` |
| 2. API | Dohoda medzi frontendom a backendom: aký vstup, aký výstup, aké HTTP kódy. | Neobsahuje logiku. | `docs/v2/api-contract.md` ↔ B10 `backend/app/api/schemas.py` |
| 3. Backend (Python) | Parsovanie, validácia, výpočet splátky a mimoriadnej splátky, formát, texty, ukladanie cez rozhranie. | Nepozná DOM; výpočet (B1–B9) nepozná HTTP ani databázu (NFR-V2-03). | `backend/app/` |
| 4. Supabase | Ukladá výpočty do tabuľky `calculations`. | Nepočíta. Prístup má iba backend (AD-V2-06). | `supabase/migrations/`, B13 |

Zdroje pravdy sa nemenia: požiadavky `01-functional.md`, moduly a rozhodnutia `02-architecture.md`, JSON `api-contract.md`, implementačné detaily `02a-tiers.md`. Tento dokument určuje iba **poradie, testy, kritériá hotovosti a commity**.

**Vzťah k 03 a 04:** CLAUDE.md predpisuje poradie 03 → 04 → 05. Tento plán vznikol skôr na výslovnú požiadavku používateľky (2026-10-22). Aby sa poradie nestratilo:
- každý krok obsahuje zoznam testov s menami a ID požiadaviek, z ktorých sa dá `03-test-scenarios.md` V2 vytvoriť mechanicky (krok 13);
- pred krokom 1 sa odporúča review tohto plánu v čistej session (experiment E2 vo V1: čistý kontrolór našiel 82 % problémov, autorský 64 %).

**Stav krokov (aktualizuje sa po každom commite):**

| Krok | Vrstva | Stav |
|------|--------|------|
| 0 | dokumentácia | hotové (`577f910`) |
| 1 | 3. Backend (jadro) | hotové |
| 2 | 3. Backend (jadro) | hotové |
| 3 | 3. Backend (jadro) | hotové |
| 4 | 3. Backend (jadro) | hotové |
| 5 | 3. Backend (jadro) | čaká |
| 6, 8 | 2. API | čaká |
| 7 | 4. Supabase (kód) | čaká |
| 9, 10 | 1. Frontend | čaká |
| 11 | e2e (1 + 2 + 3) | čaká |
| 12 | 4. Supabase naživo | čaká na používateľku |
| 13 | uzavretie | čaká |

---

## 1. Východisko (stav k 2026-10-22, commit `4ceb666`)

`pytest`: **196 testov, všetky prechádzajú.** E2E testy neexistujú. Supabase nie je založená, `backend/.env` neexistuje.

| Vrstva | Hotové | Chýba |
|--------|--------|-------|
| Frontend | FR-01 až FR-05, debounce 300 ms, zahodenie staršej odpovede, timeout 5 s, stav `unavailable` (OQ-V2-04) | Polia IN-04 až IN-06, výsledky FR-06 až FR-08, chyby FR-09, tlačidlo FR-10, zoznam FR-11, Playwright e2e |
| API | `POST /api/calculate` bez kľúča `extra`, `GET /api/health` | `extra` v požiadavke a odpovedi, `FieldKey` s `extraMonth`/`extraAmount`, `POST /api/calculations`, `GET /api/calculations`, 503 handler |
| Backend | B1, B2–B5, B7–B9 pre IN-01 až IN-03 a FR-01 až FR-05; B12 `save`; B13 `save`; B14; B15 | B2 hranice IN-04/IN-05, B3 `validate_extra_against_loan`, B4 `balance_after`, B5 `round_down`, **B6**, B7 `format_rate`, **B7a**, B8 správy FR-09/FR-10/FR-11 a tvary slov, B9 s mimoriadnou splátkou, B12/B13 `list_latest` a stĺpce `extra_*` |
| Supabase | Migrácia S1 (overená parserom `pglast`), klient s timeoutom 4 s | Projekt, spustená migrácia, `backend/.env`, ručný test 4.4 z `02a-tiers.md` |

Nesúlady v dokumentoch, ktoré rieši krok 0:
- `02-architecture.md`, Stack: frontend „natívne ES moduly“ a tabuľka „Čo sa presúva z V1“ s `frontend/js/*.js` – neplatí od AD-V2-13 (jeden súbor).
- `02-architecture.md`, Dependency Direction, pravidlo 7: hľadá výskyty vo `frontend/js/` – má byť `frontend/index.html`.
- `02-architecture.md`, Stack: `tzdata` je v zozname závislostí, v `backend/requirements.txt` nie je (treba pre B7a na Windows).
- OQ-V2-04 (text stavu `unavailable`) nie je vo `01-functional.md`; OQ-V2-05 (`SavedExtra`, `SavedRecord`) nie je v `02-architecture.md`.

---

## 2. Rozhodnutia pred začiatkom

**Všetky rozhodnutia sú prijaté podľa návrhu (používateľka, 2026-10-22).** RP-01 je zapísané ako AD-V2-15 v `02-architecture.md`. Kroky, ktoré od rozhodnutia závisia, sú v stĺpci „Blokuje“.

| ID | Otázka | Možnosti | Návrh | Blokuje |
|----|--------|----------|-------|---------|
| RP-01 | AD-V2-14 (automatické ukladanie každého platného výpočtu) a FR-10 (tlačidlo „Uložiť výpočet“) sa vylučujú. Pri písaní vzniká 1 riadok pri každej pauze ≥ 300 ms, takže zoznam FR-11 (20 riadkov) zaplnia rozpísané hodnoty. | **A** Vrátiť AD-V2-07: ukladá sa iba po kliknutí. **B** Ponechať AD-V2-14, FR-10 zrušiť. **C** Ponechať oboje, automatické ukladanie iba pri zmene hodnôt. | **Rozhodnuté: A** (AD-V2-15). FR-10 a FR-11 tak platia bez zmeny a 1 klik = 1 riadok je testovateľný. Pri B treba prepísať FR-10, pri C pribudne stav v backende. | 8, 10 |
| RP-02 | OQ-V2-01: zoznam spoločný, alebo s prihlásením? | Spoločný / Supabase Auth | **Rozhodnuté:** spoločný (EP-V2-03 zostane mimo V2). | 7, 8 |
| RP-03 | OQ-V2-03: predvolený režim IN-06. | Kratšia doba / Nižšia splátka | **Rozhodnuté:** Kratšia doba. | 9 |
| RP-04 | Nástroj pre e2e. | `@playwright/test` (Node.js v24.20.0 je nainštalovaný) / `pytest-playwright` | **Rozhodnuté:** `@playwright/test`, ako určuje 02 Stack. `package.json` iba s `devDependencies` v koreni repozitára. | 11 |
| RP-05 | OQ-V2-06: premenovať `02a-tiers.md`? | Áno → `02a-tiers.md` / nie | **Rozhodnuté:** áno, premenované v kroku 0. | 0 |

---

## 3. Kroky

Pravidlá pre každý krok:
- 1 krok = 1 commit + push (CLAUDE.md, pravidlo 4). Správa commitu je uvedená pri kroku.
- Krok je hotový, keď prejde **celý** `pytest` (z `backend/`: `.venv/Scripts/python.exe -m pytest`), nie iba nové testy.
- Každý nový test uvádza ID požiadavky v mene alebo docstringu (CLAUDE.md, pravidlo 3).
- Počty testov sú minimálne. Ak krok pridá menej testov, ako je uvedené, nie je hotový.

### Krok 0 – Zosúladenie dokumentov (bez kódu)

| | |
|---|---|
| **Vrstva** | dokumentácia |
| **Zmeny** | `02-architecture.md`: Stack a „Čo sa presúva z V1“ podľa AD-V2-13; pravidlo 7 na `frontend/index.html`; Data Model doplniť o `SavedExtra` a `SavedRecord` (OQ-V2-05); AD podľa RP-01. `01-functional.md`: text OQ-V2-04 do FR-05; RP-03 ako rozhodnutie. Premenovanie podľa RP-05 vrátane odkazov v `CLAUDE.md` a `handoff.md`. |
| **Hotové, keď** | `grep -rn "frontend/js" docs/v2` vráti 0 riadkov mimo histórie; OQ-V2-04 až OQ-V2-06 majú stav „Rozhodnuté“. |
| **Commit** | `Plán V2: zosúladenie 01 a 02 s AD-V2-13 a rozhodnutiami RP-01 až RP-05` |

### Krok 1 – Backend: vstupy mimoriadnej splátky (B2, B3)

| | |
|---|---|
| **Vrstva** | 3. Backend (jadro) |
| **Požiadavky** | IN-04, IN-05, IN-06, FR-09 |
| **Zmeny** | B2 `limits.py`: `extra_month {min 1, max 359, decimals 0}`, `extra_amount {min 100, max 1 000 000, decimals 2}`. B3 `validate.py`: `RawInput` + `extra_month`, `extra_amount`, `mode`; pravidlo „obe prázdne = bez mimoriadnej splátky“; `validate_extra_against_loan(month, amount, n, balance_floor)`. B3 neimportuje doménu. |
| **Testy (≥ 14)** | `test_in04_hranice` (`1`, `359` platné; `0`, `360`, `1,5`, `abc` neplatné); `test_in04_pri_1_roku` (`11` platné, `12` neplatné cez `validate_extra_against_loan`); `test_in05_hranice` (`100`, `10 000` platné; `99,99`, `100,005`, `abc` neplatné); `test_in05_menej_ako_zostatok` (`98238,95` platné, `98238,96` neplatné pri floor 98 238,96); `test_fr09_obe_prazdne_nie_je_chyba`; `test_fr09_iba_jedno_vyplnene` (2 prípady); `test_fr09_poradie_kontrol` (prázdne → nan → step → range). |
| **Hotové, keď** | Všetky existujúce testy B3 pre IN-01 až IN-03 prechádzajú bez zmeny očakávaní. |
| **Commit** | `Backend V2: vstupy IN-04 až IN-06 v B2 a B3 (FR-09)` |

### Krok 2 – Backend: zostatok a zaokrúhlenie nadol (B4, B5)

| | |
|---|---|
| **Vrstva** | 3. Backend (jadro) |
| **Požiadavky** | DR-05, IN-05 (hranica), DR-03 |
| **Zmeny** | B4 `balance_after(params, months)` podľa DR-05, bez zaokrúhľovania. B5 `round_down(value, decimals=2)` cez `Decimal(repr(x))` a `ROUND_FLOOR`, s pravidlom \|x\| < 1e-6 → 0. |
| **Testy (≥ 8)** | `test_dr05_b12` = 98 238,9636 ± 1e-4; `test_dr05_b60` = 90 447,51 (po `round_half_up`); `test_dr05_b6_nulova_sadzba` = 6 000,00; `test_dr05_b1_20_percent` = 999 956,48; `test_dr05_b_n_je_nula` (\|B_360\| < 1e-6); `test_round_down_98238_9636` = 98 238,96; `test_round_down_nikdy_minus_nula`; `test_round_down_1_009` = 1,00. |
| **Commit** | `Backend V2: balance_after (DR-05) a round_down (IN-05)` |

### Krok 3 – Backend: modul B6 mimoriadna splátka

| | |
|---|---|
| **Vrstva** | 3. Backend (jadro) |
| **Požiadavky** | FR-06, FR-07, FR-08, DR-06 až DR-09 |
| **Zmeny** | Nový `app/domain/extra_payment.py`: `ExtraParams`, `ExtraResultRaw`, `calculate_extra(params, extra)`. Kratšia doba: cyklus po mesiacoch od B'_K, posledná splátka `B·(1+i)`, zostatok ≤ 1e-6 = 0. Nižšia splátka: DR-08, pri 0 % `B'_K / (n − K)`. Ušetrený úrok = úrok FR-03 − nový úrok, oba nezaokrúhlené. Importuje iba B4. |
| **Testy (≥ 12)** | `test_dr10_kratsia_doba[1..4]` a `test_dr10_nizsia_splatka[1..4]` – 8 riadkov DR-10, každá hodnota po `round_half_up` presne; `test_fr08_nulova_sadzba_usetri_0`; `test_dr07_cyklus_konci_najviac_po_n_splatkach` (K = 1, E = 100, 1 000 000 €, 20 %); `test_b6_nezaokruhluje` (výsledok nie je `Decimal`); `test_b6_importuje_iba_b4` (rozšírenie `test_architecture.py`). |
| **Hotové, keď** | 8/8 riadkov DR-10 sa zhoduje na 0,01 €. |
| **Commit** | `Backend V2: B6 mimoriadna splátka (FR-06 až FR-08, DR-06 až DR-10)` |

### Krok 4 – Backend: texty a formát (B7, B8)

| | |
|---|---|
| **Vrstva** | 3. Backend (jadro) |
| **Požiadavky** | FR-06 (text počtu splátok), FR-09 (správy), FR-11 (sadzba, tvary slov) |
| **Zmeny** | B7 `format_rate(4)` → `"4,00 %"`. B8: `plural(n, 'mesiac')`, správy FR-09 podľa tabuľky v `01-functional.md` (5 riadkov), text `"300 mesiacov (o 60 mesiacov menej)"`, text zoznamu `"10 000,00 € v 12. mesiaci, kratšia doba"`, `"30 rokov"`. |
| **Testy (≥ 16)** | `test_plural` pre 0, 1, 2, 4, 5, 60, 300 (mesiac aj rok); `test_fr09_sprava_in04` („…od 1 do 359.“); `test_fr09_sprava_in05_so_zostatkom` („…menej ako zostatok úveru 98 238,96 €.“); `test_fr09_sprava_in05_bez_zostatku`; `test_fr09_sprava_zostatok_pod_100` („V mesiaci 359 je zostatok úveru 2,77 €…“); `test_fr06_text_splatok`; `test_fr11_text_extra` (oba režimy); `test_fr11_format_rate` (`0` → `"0,00 %"`, `20` → `"20,00 %"`, `3.5` → `"3,50 %"`). |
| **Commit** | `Backend V2: texty FR-06, FR-09, FR-11 a format_rate (B7, B8)` |

### Krok 5 – Backend: orchestrácia B9 s mimoriadnou splátkou

| | |
|---|---|
| **Vrstva** | 3. Backend (jadro) |
| **Požiadavky** | FR-01 až FR-09 end-to-end, DR-04, DR-10, FR-10 (`SavedValues`), NFR-V2-02 |
| **Zmeny** | B9 podľa tabuľky 3.2 v `02a-tiers.md` (kroky 1–8). `Results.extra`, `SavedExtra` v `SavedValues`. Horná hranica IN-04 je 359, ak je IN-03 neplatný. Pri chybe IN-01 až IN-03 a súčasne neplatnom IN-05 správa „…od 100 do 1 000 000 €.“ |
| **Testy (≥ 18)** | `test_dr04_akceptacia[1..4]` (zostávajú); `test_dr10_akceptacia[1..8]` – texty presne podľa tabuliek DR-10; `test_fr09_tabulka[1..5]` – každý riadok tabuľky FR-09; `test_fr09_ziadne_vysledky_pri_chybe`; `test_fr10_saved_extra_zaokruhlene` (riadok 1 DR-10 → `interest_saved = Decimal('18797.02')`); `test_nfr_v2_02` (K = 1, 30 rokov, medián zo 100 ≤ 50 ms). |
| **Hotové, keď** | Výpočet (B1–B9) je úplný; `test_architecture.py` potvrdí 0 importov `fastapi`, `pydantic`, `supabase`, `app.api`, `app.db` v B1–B9 (NFR-V2-03). |
| **Commit** | `Backend V2: B9 s mimoriadnou splátkou, akceptačné testy DR-10` |

### Krok 6 – API: kľúč `extra` (B10, B11) + frontend posiela `extra`

| | |
|---|---|
| **Vrstva** | 2. API (+ minimálna zmena 1. Frontend) |
| **Požiadavky** | API-R2, API-R3, API-R5, API-R6, FR-06 až FR-09 |
| **Zmeny** | B10: `ExtraRequest {month, amount, mode: Literal[...]}`, `ExtraResult` (2 tvary podľa `mode`), `FieldKey` + `extraMonth`, `extraAmount`. B11 odovzdá `extra` do `RawInput` a prevedie kľúče chýb na camelCase. **V tom istom commite** F4 `readForm()` posiela `extra: {month: '', amount: '', mode: 'shorter_term'}` – inak by frontend po tomto kroku dostával 422, lebo `extra` je povinný kľúč (API-R6). |
| **Testy (≥ 10)** | `test_api_priklad_ok_kratsia_doba` a `test_api_priklad_ok_nizsia_splatka` (presné JSON z `api-contract.md`); `test_api_extra_null_ked_prazdne`; `test_api_invalid_extra_amount`; `test_api_422_bez_extra`; `test_api_422_neznamy_mode`; `test_api_422_extra_navyse_kluc`; `test_api_ok_nema_errors` a `test_api_invalid_nema_results` (invarianty); `test_frontend_posiela_extra` (statický test v `test_frontend.py`). |
| **Hotové, keď** | Každý JSON príklad z `api-contract.md` a z časti 2.2 `02a-tiers.md` má 1 test; prehliadač na `http://127.0.0.1:8000/` počíta ako pred krokom. |
| **Commit** | `API V2: kľúč extra v POST /api/calculate (B10, B11)` |

### Krok 7 – Supabase vrstva v kóde: čítanie a stĺpce `extra_*` (B12, B13)

| | |
|---|---|
| **Vrstva** | 4. Supabase (prístup cez backend) |
| **Požiadavky** | FR-10, FR-11, NFR-V2-07 |
| **Zmeny** | B12: `list_latest(limit=20)` v `CalculationRepository` a `InMemoryRepository` (od najnovšieho). B13: `to_row` so 9 stĺpcami `extra_*` (všetky `None`, ak `extra is None`), `from_row` → `SavedRecord`, `list_latest` cez `select('*').order('created_at', desc=True).limit(20)`; každá chyba → `StorageError`. |
| **Testy (≥ 10)** | `test_inmemory_list_latest_20_z_25`; `test_inmemory_list_poradie`; `test_inmemory_fail`; `test_to_row_17_stlpcov_bez_id_a_created_at`; `test_to_row_extra_null_vsetky_extra_none` (constraint `extra_all_or_nothing`); `test_to_row_sumy_ako_text`; `test_list_latest_url_a_parametre` (MockTransport: `order=created_at.desc`, `limit=20`); `test_from_row_round_trip`; `test_list_latest_chyby` (7 typov chýb → `StorageError`). |
| **Commit** | `Supabase V2: list_latest a stĺpce extra_* v B12 a B13` |

### Krok 8 – API: uloženie a zoznam (B7a, B10, B11, B14)

| | |
|---|---|
| **Vrstva** | 2. API + 3. Backend |
| **Požiadavky** | FR-10, FR-11, API-R5, API-R6, AD-V2-12; podľa RP-01 |
| **Zmeny** | `tzdata` do `requirements.txt` s presnou verziou. B7a `format_datetime(utc)` → `"15. 10. 2026 14:05"` v Europe/Bratislava. B10: `SaveResponse`, `SavedCalculation`, `CalculationList`, `StorageErrorBody`. B11: `POST /api/calculations` (výpočet znova, 201 / 422 / 503) a `GET /api/calculations` (200 / 503). B14: 1 `exception_handler(StorageError)` → 503 `{"error": "storage_unavailable"}`. Podľa AD-V2-15 z `POST /api/calculate` odstrániť `BackgroundTasks`; `README.md` a `backend/README.md` už nespomínajú automatické ukladanie. |
| **Testy (≥ 12)** | `test_b7a_leto` (UTC 12:05 v júli → 14:05) a `test_b7a_zima` (UTC 13:05 v januári → 14:05); `test_b7a_format_bez_nul` (`5. 1. 2026`); `test_post_calculations_201`; `test_post_calculations_ulozi_1_zaznam`; `test_post_calculations_422_neplatny_vstup`; `test_post_calculations_503`; `test_post_calculations_ignoruje_vysledky_klienta` (AD-V2-12: neznámy kľúč → 422); `test_get_calculations_prazdny`; `test_get_calculations_20_z_25`; `test_get_calculations_tvar_savedcalculation`; `test_get_calculations_503`; `test_calculate_neuklada` (AD-V2-15). |
| **Hotové, keď** | `GET /docs` ukazuje 4 endpointy; každý riadok tabuliek kódov v `api-contract.md` má 1 test. |
| **Commit** | `API V2: POST a GET /api/calculations, B7a, 503 handler` |

### Krok 9 – Frontend: mimoriadna splátka

| | |
|---|---|
| **Vrstva** | 1. Frontend |
| **Požiadavky** | FR-06 až FR-09 (zobrazenie), IN-04 až IN-06, NFR-V2-04, NFR-V2-05 |
| **Zmeny** | V `frontend/index.html`: `<fieldset>` „Mimoriadna splátka“ s `<legend>`, IN-04 a IN-05 ako `type="text" inputmode="decimal"`, 2× `radio` IN-06 (predvolené podľa RP-03), blok výsledkov `extra` (iba ak `results.extra !== null`), chyby pri `extraMonth` a `extraAmount` s `aria-invalid` a `aria-describedby`. Zmena režimu spustí výpočet (udalosť `change`). Atribúty `data-*` podľa časti 1.3 `02a-tiers.md`. |
| **Testy (≥ 6, statické)** | `test_nfr_v2_04_fieldset_legend`; `test_nfr_v2_04_kazdy_vstup_ma_label` (5 polí + 2 radio); `test_nfr_v2_05_ziadne_cisla_hranic` (0 výskytov `359`, `100`, `1000000` v skripte); `test_nfr_v2_05_ziadne_externe_zdroje`; `test_frontend_data_atributy_extra`; `test_frontend_predvoleny_rezim`. |
| **Ručne v prehliadači** | 8 riadkov DR-10 zadať a porovnať texty; 375 px bez vodorovného posunu; svetlý aj tmavý režim. |
| **Commit** | `Frontend V2, 2. časť: mimoriadna splátka (FR-06 až FR-09)` |

### Krok 10 – Frontend: uloženie a zoznam

| | |
|---|---|
| **Vrstva** | 1. Frontend |
| **Požiadavky** | FR-10, FR-11, API-R7, NFR-V2-04 |
| **Zmeny** | F5: `saveCalculation`, `listCalculations`, mapovanie 201/503/422/sieť/timeout podľa 1.6 `02a-tiers.md`. F3: `refreshList()` pri načítaní a po uložení, stav `saving`. F4: tlačidlo aktívne iba v stave `ok`, správy FR-10 v `role="status"`, tabuľka 20 riadkov, prázdny stav, chyba načítania. Zmena `test_frontend_iba_jedno_volanie_fetch`: `fetch(` stále iba v oddiele F5, povolené cesty sú 3. |
| **Testy (≥ 4, statické)** | `test_frontend_fetch_iba_v_f5`; `test_frontend_fetch_iba_3_cesty_api`; `test_nfr_v2_04_save_role_status`; `test_frontend_data_atributy_zoznam`. |
| **Commit** | `Frontend V2, 3. časť: uloženie výpočtu a zoznam (FR-10, FR-11)` |

### Krok 11 – E2E testy (Playwright)

| | |
|---|---|
| **Vrstva** | 1. Frontend + 2. API + 3. Backend spolu |
| **Požiadavky** | FR-01 až FR-11, NFR-V2-01, NFR-V2-04, API-R7, R-V2-04 |
| **Zmeny** | `package.json` v koreni iba s `devDependencies: {"@playwright/test": "<presná verzia>"}` a skriptom `test:e2e`; `playwright.config.js` s `webServer` = `backend/.venv/Scripts/python.exe -m uvicorn app.main:app` v `backend/`, `env: {STORAGE: 'memory'}`, `retries: 0`, 1 prehliadač (Chromium); `.gitignore` + `node_modules/`, `test-results/`. README: inštalácia `npm ci` a `npx playwright install chromium`. |
| **Testy (≥ 14)** | `FR-01: predvyplnené hodnoty → 477,42 €`; `FR-05: 2 chyby naraz, výsledky skryté`; `NFR-V2-01: výsledok do 500 ms po poslednej zmene`; `AD-V2-02: 6 rýchlych zmien = 1 požiadavka`; `R-V2-04: staršia odpoveď sa zahodí` (`page.route` so spomalením); `API-R7: timeout 5 s → stav unavailable`; `OQ-V2-04: Skúsiť znova obnoví výpočet`; `FR-06: riadok 1 DR-10`; `FR-07: riadok 1 DR-10`; `FR-09: iba IN-04 vyplnený → správa pri IN-05`; `FR-10: 1 klik = 1 záznam` (2 rýchle kliky → 1 riadok v zozname); `FR-10: tlačidlo neaktívne pri chybe`; `FR-10: 503 → správa, formulár zostane`; `FR-11: prázdny zoznam → správa`; `FR-11: 25 uložení → 20 riadkov`; `NFR-V2-04: aria-invalid a aria-describedby`. |
| **Hotové, keď** | `npm run test:e2e` prejde 3 z 3 behov za sebou (R-05 V1, 0 % flaky). |
| **Commit** | `E2E V2: Playwright testy FR-01 až FR-11` |

### Krok 12 – Supabase naživo (ručný krok používateľky)

| | |
|---|---|
| **Vrstva** | 4. Supabase |
| **Požiadavky** | FR-10, FR-11, NFR-V2-06, NFR-V2-07, AD-V2-06 |
| **Kto** | Založenie účtu a projektu a skopírovanie kľúča robí **používateľka** (Claude nezakladá účty ani nevkladá kľúče). Claude potom spustí overenie a zapíše výsledok. |
| **Postup** | Tabuľka 4.4 v `02a-tiers.md`, kroky 1–5: projekt `eu-central-1`, migrácia S1 v SQL Editore, `backend/.env`, 1 uloženie cez UI, kontrola anon kľúča. Navyše: 21 uložení → `GET /api/calculations` vráti 20. |
| **Hotové, keď** | V tabuľke je riadok s `monthly_payment = 477.42`; riadok s mimoriadnou splátkou má 9 stĺpcov `extra_*` vyplnených podľa riadku 1 DR-10; anon kľúč dostane `[]`; uloženie aj zoznam ≤ 2 s (NFR-V2-07); `git status` neukazuje `.env`; `test_secrets.py` prechádza. |
| **Commit** | `Supabase V2: overenie proti skutočnej databáze` (iba `handoff.md` a README, žiadne tajné údaje) |

### Krok 13 – Uzavretie: dokumenty a review kódu

| | |
|---|---|
| **Vrstva** | všetky |
| **Zmeny** | `03-test-scenarios.md` V2 z testov krokov 1–12 (tabuľka Test / Úroveň / Modul / Požiadavka / Vstup / Očakávaný výstup); `/code-review` a `/simplify` nad zmenami V2; matica sledovateľnosti v 02 overená proti testom; `06-retro.md` V2 (plán vs. skutočnosť: počet testov, odchýlky). |
| **Hotové, keď** | Každá požiadavka z časti 4 má ≥ 1 test; `pytest` aj `test:e2e` prechádzajú. |
| **Commit** | `Plán V2: 03-test-scenarios a uzavretie` |

---

## 4. Sledovateľnosť: požiadavka → krok

| Požiadavka | Kroky |
|------------|-------|
| FR-01 až FR-05 | hotové; regresia v 5, 6, 11 |
| FR-06, FR-07 | 3, 4, 5, 6, 9, 11 |
| FR-08 | 3, 5, 6, 11 |
| FR-09 | 1, 4, 5, 6, 9, 11 |
| FR-10 | 5, 7, 8, 10, 11, 12 |
| FR-11 | 4, 7, 8, 10, 11, 12 |
| IN-04 až IN-06 | 1, 2, 6, 9 |
| DR-05 až DR-10 | 2, 3, 5 |
| API-R1 až API-R7 | 6, 8, 10, 11 |
| NFR-V2-01 | 11 |
| NFR-V2-02 | 5 |
| NFR-V2-03 | 3, 5 (test architektúry) |
| NFR-V2-04 | 9, 10, 11 |
| NFR-V2-05 | 9, 10 |
| NFR-V2-06 | 12 (+ existujúci `test_secrets.py`) |
| NFR-V2-07 | 7, 12 |
| NFR-V2-08 | hotové; overí 11 (`webServer`) |

## 5. Poradie a závislosti

```
0 ─► 1 ─► 2 ─► 3 ─► 4 ─► 5 ─► 6 ─► 9 ─┐
                         └─► 7 ─► 8 ─► 10 ─► 11 ─► 13
                                   └────────► 12 ─┘
```

- Kroky 1 až 5 menia iba jadro backendu, frontend a API sa nedotknú.
- Krok 7 (úložisko) potrebuje iba `SavedExtra` z kroku 5, preto môže bežať súbežne s krokom 6.
- Krok 12 sa dá urobiť kedykoľvek po kroku 8; čaká iba na používateľku.

## 6. Definition of Done V2

| # | Kritérium | Meranie |
|---|-----------|---------|
| D-V2-01 | Všetky testy backendu prechádzajú. | `pytest`: 0 zlyhaní, ≥ 196 + 110 = 306 testov. |
| D-V2-02 | E2E prechádzajú stabilne. | `npm run test:e2e`: 3 z 3 behov, ≥ 14 testov. |
| D-V2-03 | Výpočet sa zhoduje so špecifikáciou. | 4/4 riadky DR-04 a 8/8 riadkov DR-10 na 0,01 €. |
| D-V2-04 | Vrstvy sú oddelené. | 0 zakázaných importov v B1–B9; `fetch(` iba v F5; 0 hraníc a vzorcov vo frontende. |
| D-V2-05 | Výkon. | `POST /api/calculate` medián ≤ 50 ms; výsledok v prehliadači ≤ 500 ms po poslednej zmene; uloženie a zoznam ≤ 2 s. |
| D-V2-06 | Tajné údaje. | 0 výskytov kľúča v gite a vo `frontend/`. |
| D-V2-07 | Dokumenty sedia s kódom. | Každá zmena B10 je v `api-contract.md`; `handoff.md` aktualizovaný po každom kroku. |

## 7. Riziká

| # | Riziko | Opatrenie |
|---|--------|-----------|
| R-P-01 | Krok 6 rozbije frontend (povinný kľúč `extra` → 422). | Frontend sa mení v tom istom commite; ručná kontrola v prehliadači je súčasťou „Hotové, keď“. |
| R-P-02 | Cyklus DR-07 sa pri zaokrúhľovacej chybe zastaví o 1 splátku neskôr. | Prah 1e-6 € (rovnaký ako B5); test riadku 4 DR-10 (358 splátok) a test „najviac n splátok“. |
| R-P-03 | B7a dáva na Windows chybu `ZoneInfoNotFoundError`. | `tzdata` v `requirements.txt` (krok 8), test leto/zima. |
| R-P-04 | Playwright na Windows nestabilný pri štarte servera. | `webServer.url` na `/api/health`, `timeout` 30 s, `retries: 0` – každé zlyhanie sa rieši, nie opakuje. |
| R-P-05 | Supabase projekt sa po 7 dňoch pozastaví (R-V2-03). | Krok 12 až tesne pred uzavretím; postup obnovenia v README. |
| R-P-06 | RP-01 sa nerozhodne a krok 8 sa urobí s automatickým ukladaním. | Krok 8 nezačne bez zapísaného RP-01 v 02. |

## 8. Príkazy

```bash
# backend testy (z backend/)
.venv/Scripts/python.exe -m pytest

# spustenie bez Supabase (z backend/)
STORAGE=memory .venv/Scripts/python.exe -m uvicorn app.main:app

# e2e (z koreňa, od kroku 11)
npm run test:e2e
```
