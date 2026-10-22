# Handoff

## V2 – prechod na 4 časti (frontend, API, backend FastAPI, Supabase)

### Aktuálny stav V2
- Používateľka chce kalkulačku prerobiť na 4 časti. Kód zatiaľ neexistuje ani vo V1, takže V2 sa plánuje rovno, bez prepisovania kódu.
- Hotové: `docs/v2/01-functional.md`:
  - FR-01 až FR-05, IN-01 až IN-03 a DR-01 až DR-04 sú prevzaté z V1 bez zmeny;
  - nové požiadavky FR-06 až FR-11 (mimoriadna splátka v 2 režimoch, ušetrený úrok, chyby, uloženie, zoznam 20 výpočtov);
  - nové vstupy IN-04 až IN-06 a pravidlá DR-05 až DR-10;
  - 8 referenčných príkladov overených dvoma nezávislými výpočtami (cyklus po mesiacoch aj uzavretý vzorec, zhoda na 4 desatinné miesta);
  - otvorené otázky OQ-V2-01 až OQ-V2-03.
- Hotové: `docs/v2/02-architecture.md`:
  - 22 modulov: B1 až B15, B7a, S1, F1 až F5;
  - mapovanie M1 až M12 z V1 na nové moduly;
  - pravidlá závislostí, dátový model a SQL tabuľky `calculations`;
  - NFR-V2-01 až NFR-V2-08, rozhodnutia AD-V2-01 až AD-V2-12 a riziká R-V2-01 až R-V2-05.
- Hotové: `docs/v2/api-contract.md` – endpointy `POST /api/calculate`, `POST /api/calculations`, `GET /api/calculations` a `GET /api/health`, pravidlá API-R1 až API-R7.
- Hotové: `docs/v2/02a-tiers.md` (pôvodne `01-architecture-v2.md`) – implementačný pohľad po 4 vrstvách (frontend, API, backend, Supabase): atribúty DOM a stavy UI, kompletné JSON príklady vrátane 422, kostra Pydantic modelov B10, endpointy B11, pripojenie Supabase s timeoutom 4 s, mapovanie 17 stĺpcov, postup založenia projektu. Nové otvorené body OQ-V2-04 až OQ-V2-06.
- Oproti prvému návrhu v chate je jeden endpoint pre výpočet aj mimoriadnu splátku namiesto dvoch (AD-V2-04).
- **Hotové: backend V2, 1. časť** (`backend/`, Python 3.13, FastAPI 0.143.1):
  - moduly B1–B5, B7–B11, B14 podľa `02-architecture.md`; výpočet prenesený zo špecifikácie V1 (DR-01 až DR-04), lebo JS kód V1 nikdy nevznikol;
  - `POST /api/calculate` a `GET /api/health` podľa `api-contract.md`; kľúč `extra` v požiadavke zatiaľ nie je (pribudne s B6), v odpovedi je vždy `extra: null`;
  - 124 testov `pytest` (scenáre M1–M8 z `docs/v1/03-test-scenarios.md`, API, NFR-V2-02, NFR-V2-03), všetky prechádzajú;
  - hodnoty označené v 03 V1 ako NEOVERENÉ sú overené nezávislým výpočtom s presnosťou 60 číslic a všetky sedia;
  - TQ-01 zapracované ako `ValueError` (Python ekvivalent `RangeError`);
  - B1 navyše akceptuje nezalomiteľné medzery U+00A0 a U+202F.
- **Hotové: príprava Supabase:**
  - migrácia S1 `supabase/migrations/20261015120000_create_calculations.sql` (presne SQL z 02, overená parserom PostgreSQL `pglast`, proti skutočnej databáze zatiaľ nespustená);
  - B15 `backend/app/config.py` (`STORAGE`, `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, chyba uvádza názov chýbajúcej premennej) a `backend/.env.example`;
  - B13 (časť) `backend/app/db/supabase_client.py` – klient s timeoutom 4 s; zatiaľ ho nič nevolá;
  - návod na nastavenie Supabase a premenných v `README.md`;
  - 160 testov prechádza (nové: config, klient bez siete, NFR-V2-06, migrácia, pravidlo 4 závislostí).
  - Zmena oproti 02: migrácia je v `supabase/migrations/` namiesto `backend/db/migrations/` (požiadavka používateľky, 02 a 02a-tiers upravené).
- **Hotové: frontend V2, 1. časť** – `frontend/index.html` (jeden súbor, AD-V2-13), FR-01 až FR-05:
  - rozhodnutia používateľky: jeden HTML súbor, čistý minimalistický vzhľad (svetlý aj tmavý režim, mobil), výpočet 300 ms po písaní, pri nedostupnom backende správa a „Skúsiť znova“ (OQ-V2-04), zatiaľ iba základný výpočet;
  - overené v prehliadači: predvyplnené hodnoty, 2 chyby naraz, 6 rýchlych zmien = 1 požiadavka, staršia odpoveď sa zahodí, chyba siete, timeout 5 s, obnovenie, 375 px bez vodorovného posunu;
  - 8 statických testov v `backend/tests/test_frontend.py` (spolu 168 testov); Playwright e2e zatiaľ nie sú;
  - `.claude/launch.json` spúšťa backend na porte 8000 pre náhľad v prehliadači.
- **Hotové: ukladanie do Supabase (AD-V2-14, nahrádza AD-V2-07):**
  - `POST /api/calculate` uloží každý platný výpočet ako nový riadok v `calculations`; ukladá sa v `BackgroundTasks` po odoslaní odpovede, chyba databázy sa iba zapíše do logu;
  - B9 vracia `CalculationOutcome` (`response` + `SavedValues` zaokrúhlené na 0,01 €), B12 `repository.py` (`CalculationRepository`, `InMemoryRepository`, `StorageError`), B13 `supabase_repository.py`, B14 vyberá úložisko pri štarte (`lifespan`) podľa `STORAGE`;
  - bez `backend/.env` (a bez `STORAGE=memory`) sa backend nespustí a vypíše chýbajúcu premennú;
  - testy: 196 prechádza; Supabase sa simuluje cez `httpx.MockTransport` so skutočnou knižnicou `supabase` (overená URL, hlavičky, telo, 7 typov chýb), `tests/conftest.py` zaručí, že žiadny test nejde na internet;
  - ručne overené: pri nedostupnej Supabase odpoveď za 28 ms a v logu „Výpočet sa nepodarilo uložiť do Supabase: timed out“;
  - **neoverené proti skutočnej Supabase** – `backend/.env` zatiaľ neexistuje;
  - známy dôsledok: pri písaní vzniká riadok pri každej pauze ≥ 300 ms s platnými hodnotami (aj duplicitné).
- **Hotové: `docs/v2/05-plan.md`** (2026-10-22) – implementačný plán dokončenia 4 vrstiev: kroky 0 až 13, každý s vrstvou, ID požiadaviek, menovanými testami (spolu ≥ 110 nových v pytest, ≥ 14 e2e), kritériom hotovosti a správou commitu; rozhodnutia RP-01 až RP-05; Definition of Done D-V2-01 až D-V2-07; riziká R-P-01 až R-P-06. Vznikol pred 03 a 04 na výslovnú požiadavku používateľky.
- Odchýlka od CLAUDE.md (pravidlo 1): kód vznikol pred `03` až `05` V2 na výslovnú požiadavku používateľky.
- Python nie je v PATH: `%LOCALAPPDATA%\Programs\Python\Python313\python.exe`, venv v `backend/.venv`.

- `05-plan.md` má od 2026-10-22 tabuľku „Stav krokov“ pod úvodom; po každom kroku sa aktualizuje.
- **Hotové: krok 0 `05-plan.md`** (2026-10-22) – používateľka prijala RP-01 až RP-05 podľa návrhu. Zapísané: AD-V2-15 (ukladá sa iba po kliknutí, nahrádza AD-V2-14; v kóde až v kroku 8, dovtedy `POST /api/calculate` ešte ukladá automaticky), OQ-V2-01 a OQ-V2-03 rozhodnuté, text OQ-V2-04 v 01, `SavedExtra` a `SavedRecord` v 02, `01-architecture-v2.md` premenovaný na `02a-tiers.md`, odkazy na `frontend/js/` opravené podľa AD-V2-13.

- **Realizácia `05-plan.md` (2026-10-22):**
  - krok 1: B2 hranice IN-04/IN-05, B3 `validate_extra_against_loan`, `ValidationResult.has_extra` a `partial`; 29 nových testov (225 spolu).
  - krok 2: B4 `balance_after` (DR-05), B5 `round_down`; 20 nových testov (245). Zistené: pri 1 000 000 €, 20 % je |B_360| = 1,4e-6 € (nad prahom 1e-6, R-P-02), test používa relatívnu toleranciu.
  - krok 3: B6 `app/domain/extra_payment.py`; 8/8 riadkov DR-10 sedí na 0,01 € hneď na prvý pokus; cyklus DR-07 má strop n − K splátok (R-P-02); 24 nových testov.
  - krok 4: B7 `format_rate`, B8 `plural`, správy FR-09 (`extra_month_message`, `extra_amount_message`), `payments_text`, `years_text`, `extra_text`; 31 nových testov (302).
  - krok 5: B9 s mimoriadnou splátkou (`ExtraResult`, `SavedExtra`, správy FR-09 podľa kontextu); 8/8 DR-10 a 9 riadkov FR-09 ako akceptačné testy; 23 nových testov (325).
  - krok 6: B10 `ExtraInput`, `ShorterTermResult`, `LowerPaymentResult`, `FieldKey` s `extraMonth`/`extraAmount`; B11 prevod chýb na camelCase; frontend posiela `extra` (zatiaľ prázdne); staré testy API doplnené o `extra`; 21 nových testov (346). V prehliadači overené (477,42 €). `.claude/launch.json` má konfiguráciu `backend-memory` (`STORAGE=memory`), lebo `backend/.env` existuje, ale `SUPABASE_SERVICE_ROLE_KEY` je prázdny.
  - krok 7: B12 `list_latest`; B13 `to_row` s 9 stĺpcami `extra_*`, `from_row`, `list_latest`. Zistené: postgrest pri 5xx opakuje GET 3× (~7 s) – vypnuté `.retry(False)`, inak by NFR-V2-07 a timeout 5 s frontendu neplatili. 22 nových testov (368).
  - krok 8: `tzdata==2026.5` (bez neho `ZoneInfoNotFoundError` na Windows, R-P-03 potvrdené), B7a `app/format/datetime.py`, `POST /api/calculations` (201/422/503), `GET /api/calculations` (200/503), handler `StorageError` → 503 v B14; **AD-V2-15 v kóde**: `POST /api/calculate` už neukladá, `BackgroundTasks` odstránené, 5 testov AD-V2-14 nahradených; README a `backend/README.md` upravené; 385 testov.

### Ďalšie kroky V2
1. Voliteľne review `05-plan.md` v čistej session (04 V2).
2. Krok 1 z `05-plan.md` (B2, B3 – vstupy IN-04 až IN-06), potom kroky 2 až 13; po každom kroku commit, push a aktualizácia tohto súboru.
3. Krok 12 (Supabase naživo) vyžaduje, aby používateľka založila projekt a vyplnila `backend/.env`.

---

## V1

### Aktuálny stav
- Vytvorená štruktúra repozitára: `README.md`, `CLAUDE.md`, `docs/handoff.md`, `docs/v1/`.
- Hotové: `docs/v1/01-functional.md` – funkčné požiadavky V1 (FR-01 až FR-05, IN-01 až IN-03, DR-01 až DR-04, mimo rozsahu, otvorené otázky).
- Hotové: `docs/v1/02-architecture.md` – modulárna architektúra so sekciami Stack, Modules, Dependency Direction, Data Model, Extension Points & Decisions:
  - moduly M1 až M12, každý so zodpovednosťou, dôvodom zmeny, rozhraním a ID požiadaviek;
  - overenie SRP (z pôvodných 9 modulov sa oddelili hranice M2, markup M11 a štýly M12; texty správ sa presunuli do `text/`);
  - nefunkčné požiadavky NFR-01 až NFR-04;
  - rozhodnutia AD-01 až AD-09;
  - zvážené alternatívy ALT-01 (hrubé moduly, zamietnuté) a ALT-02 (konfiguračná tabuľka, odložené);
  - body rozšírenia EP-01 až EP-10 pre všetkých 10 odložených funkcií;
  - kontrola pred ďalšou vrstvou K-01 až K-06 (všetky splnené);
  - matica sledovateľnosti.
- Hotové: `docs/v1/03-test-scenarios.md` – testovacie scenáre ako tabuľky (Test, Úroveň, Modul, Overuje požiadavku, Vstup, Očakávaný výstup, Zdroj, Typ) pre M1 až M9, architektonické kontroly a e2e; pokrytie požiadaviek; otvorené otázky TQ-01 až TQ-04.
  - Číselné hodnoty označené NEOVERENÉ boli nezávisle overené v review (04). Značky v 03 ešte treba odstrániť a doplniť stĺpec Zdroj.
- **Hotové: Vrstva 4 – `docs/v1/04-review.md`. 1. kolo kontroly je uzavreté, výsledok je 0 blockerov a plán je schválený na realizáciu.**
  - Všetkých 11 referenčných hodnôt z 01 a 03 sa zhoduje s presným výpočtom (racionálna aritmetika cez `BigInt`) aj s výpočtom podľa 02.
  - 16 nálezov (0 blocker, 5 major, 11 minor): 12 prijatých, 4 zamietnuté (nálezy 7, 8, 9, 15).
  - Potvrdené rozhodnutia: AD-08 (predvyplnené hodnoty, nález 3), návrh TQ-01 (`RangeError` v M4 až M6, nález 11), oprava preklepu TQ-05 (nález 14).
  - Súhrn modulov, ktoré sa musia zmeniť pri EP-01, EP-05 a EP-09.
- OQ-01 je rozhodnutá (AD-01): výsledky sa prepočítajú pri každej zmene vstupu.
- **Hotové: Vrstva 5 – Finálny plán V1 (`docs/v1/05-plan.md`) je úspešne dokončená, commitnutá (`3f33ec4`) a pushnutá do `main`. Plán je pripravený na test kvality.** Obsah:
  - ciele C-01 až C-04 (áno/nie);
  - rozsah a tabuľka zmien z 12 prijatých nálezov 04, vrátane 13 nových testov s názvami (spolu 110 testov: 96 v Node.js cez `npm test`, 14 v prehliadači cez `npm run test:e2e`);
  - akceptačné kritériá AK-M1 až AK-E2E (zoznam testov podľa mien) a technické T-01 až T-05;
  - poradie stavby: kroky 0 až 14, každý s modulom, testami a jedným commitom;
  - Definition of Done D-01 až D-06;
  - nástroje: hook `PostToolUse` na `npm test`, skill `/end-session`, subagent na kontrolu výpočtu (kroky 6 a 9) a sledovateľnosti (krok 14), `/code-review`, `/simplify`, Playwright MCP;
  - riziká R-01 až R-09 a otvorené otázky OQ-P1, TQ-02, TQ-03.
- Zistené pri plánovaní: Python na počítači nie je nainštalovaný, preto sa `python -m http.server` nahradí skriptom `scripts/serve.js` (R-01).
- **Hotové: `docs/v1/06-retro.md` – experiment E1.** Subagent dostal iba prompt „Build a mortgage calculator.“. Jeho výstup splnil 40 z 97 scenárov z 03 (51 zlyhalo, 6 N/A). Výpočet a 0 % úrok mal správne. Zlyhal na formáte súm, hraniciach vstupov, slovenských správach a prístupnosti. Strana „s plánom“ zatiaľ nemá kód. Skutočný počet prejdených testov treba doplniť po kroku 14.
- **Hotové: `docs/v1/06-retro.md` – experiment E2** (kontrola `05-plan.md` v tej istej session vs. v čistej session). Kontrolór s autorským kontextom našiel 14 nálezov (0 blocker / 5 major / 9 minor), čistý kontrolór 20 (0 / 7 / 13). Po zlúčení je to 22 rôznych problémov: A pokryla 64 %, B 82 %. 5 majorov našli obaja. Tým je test kvality plánu `05` hotový: **plán nie je pripravený na realizáciu, kým sa neopravia majory.**
- **Hotové: opravy `05-plan.md` podľa E2** (5 spoločných majorov a R-05):
  - OQ-P1, TQ-02 a TQ-03 sú rozhodnuté podľa návrhov (`@playwright/test` v `devDependencies`, `'empty'`, `removeAttribute`) a zapracujú sa v kroku 0;
  - testy sú rozdelené: `npm test` = `node --test "tests/**/*.test.js"` (96), `npm run test:e2e` = Playwright nad `e2e/*.spec.js` (14). Overené na Node.js v24.20.0. README vyžaduje Node.js ≥ 22;
  - `test_ziadne_zavislosti` povoľuje v `devDependencies` iba `@playwright/test` a kontroluje `index.html`, iba ak existuje;
  - `/end-session` spúšťa `test:e2e` iba vtedy, keď skript existuje (od kroku 11);
  - stĺpec „Súbory“ obsahuje skill, `.gitattributes` (krok 1), konfiguráciu Playwright (krok 11), `index.html` (krok 13) a `/simplify` úpravy (krok 14), takže sedí s D-04;
  - R-05: `retries: 0`, každé zlyhanie je chyba, v kroku 14 musí `test:e2e` prejsť 3 z 3 behov. R-02 má teraz záložné riešenie cez Microsoft Edge.
- Kód zatiaľ neexistuje.

### Ďalšie kroky V1
1. Posúdiť minor nálezy z E2 (`06-retro.md`, E2, sekcia 1: 17 problémov mimo majorov).
2. Krok 0 z `05-plan.md`: zapracovať prijaté nálezy z 04 a zmeny zo sekcie 2.2 do 01, 02 a 03 (vrátane 13 nových testov, OQ-P1, TQ-02, TQ-03 a zmeny spúšťania v 02 Stack).
3. Krok 1: kostra projektu (`package.json`, `scripts/serve.js`, `README.md`, `.gitattributes`, hook na testy, skill `/end-session`).
4. Po kroku 14: doplniť do `06-retro.md` výsledok `npm test` a `npm run test:e2e` verzie s plánom.
5. Doplniť do `prompts.md` chýbajúce prompty pre 03 a 04.
