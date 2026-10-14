# Handoff

## Aktuálny stav
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
- Kód zatiaľ neexistuje.

## Ďalšie kroky
1. Test kvality plánu `05-plan.md`.
2. Rozhodnúť OQ-P1 (nástroj pre testy v prehliadači, návrh: `@playwright/test` v `devDependencies`), TQ-02 (návrh: `'empty'`) a TQ-03 (návrh: `removeAttribute`). Pozri `05-plan.md` sekcia 7.2.
3. Krok 0 z `05-plan.md`: zapracovať prijaté nálezy z 04 do 01, 02 a 03 podľa tabuľky v sekcii 2.2 (vrátane 13 nových testov a zmeny spúšťania v 02 Stack).
4. Krok 1: kostra projektu (`package.json`, `scripts/serve.js`, `README.md`, hook na testy, skill `/end-session`).
5. Po kroku 14: doplniť do `06-retro.md` výsledok `npm test` a `npm run test:e2e` verzie s plánom.
