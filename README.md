# Hypotekárna kalkulačka v2

Hypotekárna kalkulačka so 4 časťami: frontend (HTML + JS), API, backend (Python, FastAPI) a databáza Supabase.
Plán V2 je v `docs/v2/`. Hotový je výpočet FR-01 až FR-05 v backende a príprava Supabase (tabuľka a pripojenie).

## Štruktúra

- `CLAUDE.md` – pravidlá projektu
- `docs/handoff.md` – aktuálny stav a ďalšie kroky
- `docs/v1/` – plánovacie dokumenty V1 (01 až 06, `prompts.md`)
- `docs/v2/` – plán V2: `01-functional.md`, `01-architecture-v2.md`, `02-architecture.md`, `api-contract.md`, `prompts.md`
- `backend/` – Python backend (FastAPI), návod v `backend/README.md`
- `supabase/migrations/` – SQL migrácie databázy

## Nastavenie Supabase

Robí sa raz. Potrebujete bezplatný účet na [supabase.com](https://supabase.com).

### 1. Projekt
1. V dashboarde Supabase kliknite na **New project**.
2. Zvoľte región **Central EU (Frankfurt)**, zadajte heslo databázy a počkajte, kým má projekt stav **Active** (asi 2 minúty).

### 2. Tabuľka `calculations`
1. Otvorte **SQL Editor** → **New query**.
2. Vložte celý obsah súboru `supabase/migrations/20261015120000_create_calculations.sql` a kliknite na **Run**.
3. Overenie: v **Table Editor** je tabuľka `calculations` so 17 stĺpcami a so značkou **RLS enabled**.

Alternatíva so Supabase CLI: `supabase link --project-ref <ref>` a potom `supabase db push`.

### 3. Premenné prostredia

Backend číta nastavenia zo súboru `backend/.env`. Vytvorte ho z predlohy:

```bash
cp backend/.env.example backend/.env
```

Potom v `backend/.env` doplňte hodnoty z dashboardu **Project Settings → API**:

| Premenná | Kde ju nájdete | Príklad |
|----------|----------------|---------|
| `SUPABASE_URL` | **Project URL** | `https://abcdefghijkl.supabase.co` |
| `SUPABASE_SERVICE_ROLE_KEY` | **Project API keys → `service_role`** (tlačidlo **Reveal**) | dlhý reťazec začínajúci `eyJ…` |
| `STORAGE` | – | `supabase`; `memory` = bez Supabase, záznamy iba v pamäti (testy) |

Premenné nastavené priamo v prostredí (napr. v CI) majú prednosť pred `backend/.env`.

Ak pri `STORAGE=supabase` niektorá premenná chýba, backend vypíše jej názov, napr. `Chýba premenná prostredia: SUPABASE_URL.`

### Bezpečnosť kľúčov

- Kľúč **`service_role`** obchádza RLS a má plný prístup k databáze. Patrí **iba** do `backend/.env`. Nikdy ho nedávajte do `frontend/`, do gitu ani do chatu.
- Kľúč **`anon` (public)** aplikácia nepoužíva. Frontend nepristupuje k Supabase priamo, iba cez backend (AD-V2-06). Tabuľka má zapnuté RLS bez politík, takže s kľúčom `anon` sa z nej nedá nič prečítať ani zapísať.
- `backend/.env` je v `.gitignore`. Test `backend/tests/test_secrets.py` overuje, že sa súbor `.env` nedostane do gitu a že `.env.example` neobsahuje hodnoty (NFR-V2-06).
- Ak sa kľúč `service_role` predsa dostane von, vygenerujte nový v **Project Settings → API** a starý prestane platiť.

### Pozastavený projekt

Bezplatný projekt sa po 7 dňoch bez aktivity pozastaví (R-V2-03). Obnoví sa tlačidlom **Restore project** v dashboarde.

## Backend

Inštalácia, testy a spustenie: `backend/README.md`.
