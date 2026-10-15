# CLAUDE.md

## Projekt
Hypotekárna kalkulačka v2. Projekt je vo fáze plánovania V1.

## Pravidlá
1. **Najprv plán, potom kód.** Najprv vzniká plán v `docs/v1/`. Kód sa píše až v časti B.
2. **Požiadavky píšeme číslami, nie prídavnými menami.** Napríklad „výpočet do 100 ms“, nie „rýchly výpočet“.
3. **Moduly a testy sa na požiadavky odkazujú menom.** Každý modul a test uvádza identifikátor požiadavky, ktorú pokrýva (napr. `FR-01`).
4. **Po každom výstupe commit a push.**

## Dokumentácia
- `docs/handoff.md` – aktuálny stav a ďalšie kroky na pokračovanie v novej relácii.
- `docs/v1/01-functional.md` – funkčné požiadavky.
- `docs/v1/02-architecture.md` – architektúra a štruktúra projektu.
- `docs/v1/03-test-scenarios.md` – testovacie scenáre.
- `docs/v1/04-review.md` – review dokumentov vyššie.
- `docs/v1/05-plan.md` – implementačný plán.
- `docs/v1/06-retro.md` – retrospektíva.
- `docs/v1/prompts.md` – prompty použité pri plánovaní V1.

- `docs/v2/` – plán V2 (frontend, API, backend FastAPI, Supabase): `01-functional.md`, `01-architecture-v2.md` (implementačný pohľad po 4 vrstvách), `02-architecture.md`, `api-contract.md`, `prompts.md`.

Dokumenty v `docs/v1/` a `docs/v2/` sa spracúvajú v číselnom poradí. Na konci každej relácie sa aktualizuje `docs/handoff.md`.

## Kód
- `backend/` – Python backend V2 (FastAPI). Testy: `backend/.venv/Scripts/python.exe -m pytest` z priečinka `backend/`. Postup v `backend/README.md`.
- `supabase/migrations/` – SQL migrácie. Nastavenie Supabase a premenných prostredia v `README.md`.

## Konvencie
- Nikdy necommitovať tajné údaje ani súbory `.env`.
