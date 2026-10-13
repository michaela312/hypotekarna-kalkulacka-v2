# Handoff

## Aktuálny stav
- Vytvorená štruktúra repozitára: `README.md`, `CLAUDE.md`, `docs/handoff.md`, `docs/v1/`.
- Hotové: `docs/v1/01-functional.md` – funkčné požiadavky V1 (FR-01 až FR-05, IN-01 až IN-03, DR-01 až DR-04, mimo rozsahu, otvorené otázky).
- Hotové: `docs/v1/02-architecture.md` – modulárna architektúra:
  - moduly M1 až M9, každý so zodpovednosťou, rozhraním a ID požiadaviek, ktoré pokrýva;
  - nefunkčné požiadavky NFR-01 až NFR-04;
  - rozhodnutia AD-01 až AD-07;
  - matica sledovateľnosti.
- OQ-01 je rozhodnutá (AD-01): výsledky sa prepočítajú pri každej zmene vstupu.
- Kód zatiaľ neexistuje.

## Ďalšie kroky
1. Spísať testovacie scenáre v `docs/v1/03-test-scenarios.md`. Pre každú požiadavku (FR, IN, DR, NFR) uviesť scenáre s ID a modul, na ktorom sa testuje (podľa matice v 02-architecture.md).
2. Pri review (04) overiť rozhodnutia, ktoré 01-functional.md nepokrýva:
   - predvyplnené hodnoty 100 000 / 4 / 30 pri načítaní (M9);
   - jedna správa na pole pre všetky typy chýb (M6);
   - hodnoty pod 1e-6 sa zaokrúhlia na 0 (M4).
