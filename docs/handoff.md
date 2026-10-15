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
- Oproti prvému návrhu v chate je jeden endpoint pre výpočet aj mimoriadnu splátku namiesto dvoch (AD-V2-04).

### Ďalšie kroky V2
1. Rozhodnúť OQ-V2-01 (zoznam spoločný alebo s prihlásením), OQ-V2-02 (V2 nahrádza realizáciu V1) a OQ-V2-03 (predvolený režim).
2. `docs/v2/03-test-scenarios.md` – scenáre pre B1 až B15, F1 až F5, API a e2e, vrátane DR-10 a NFR-V2-01 až NFR-V2-08.
3. `docs/v2/04-review.md` → `05-plan.md` (presné verzie závislostí, inštalácia Pythonu podľa R-V2-01, založenie projektu Supabase).

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
