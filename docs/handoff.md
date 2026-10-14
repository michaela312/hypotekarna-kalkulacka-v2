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
  - Číselné očakávané hodnoty sú označené NEOVERENÉ a stĺpec Zdroj je prázdny. Hodnoty sa overia nezávisle.
- OQ-01 je rozhodnutá (AD-01): výsledky sa prepočítajú pri každej zmene vstupu.
- Kód zatiaľ neexistuje.

## Ďalšie kroky
1. Nezávisle overiť hodnoty označené NEOVERENÉ v `docs/v1/03-test-scenarios.md`, doplniť stĺpec Zdroj a značky odstrániť.
2. Pri review (04) overiť rozhodnutia, ktoré 01-functional.md nepokrýva:
   - predvyplnené hodnoty 100 000 / 4 / 30 pri načítaní (AD-08, M11);
   - jedna správa na pole pre všetky typy chýb (M7);
   - hodnoty pod 1e-6 sa zaokrúhlia na 0 (M5);
   - otvorené otázky k testom TQ-01 až TQ-03 (správanie M4 až M6 pri vstupe mimo kontraktu, vstup iba z medzier, `aria-invalid` po oprave chyby).
