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
- Kód zatiaľ neexistuje.

## Ďalšie kroky
1. Vytvoriť `docs/v1/05-plan.md` (Vrstva 5 – implementačný plán).
2. Zapracovať prijaté nálezy z `04-review.md` do 01, 02 a 03:
   - 01: pravidlo koncových núl (nález 1), preformulovanie FR-02 (nález 2), predvyplnené hodnoty po načítaní (nález 3);
   - 02: riadky EP-01, EP-05 a EP-08 (nálezy 4 až 6), matica sledovateľnosti (nález 13), príklad M6 (nález 14), opakovateľný opis overenia v M5 (nález 16);
   - 03: odstrániť značky NEOVERENÉ a doplniť Zdroj (`04`), nové testy (nálezy 1, 10, 12), úpravy testov (nález 11).
3. Otvorené zostávajú TQ-02 (vstup iba z medzier) a TQ-03 (`aria-invalid` po oprave chyby). Review (04) ich nerozhodlo.
