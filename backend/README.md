# Backend V2 (Python, FastAPI)

Implementuje FR-01 až FR-05 V2 cez `POST /api/calculate` podľa `docs/v2/api-contract.md`.
Moduly B1–B5, B7–B11 a B14 podľa `docs/v2/02-architecture.md`. Pripravené je pripojenie k Supabase (B15 `app/config.py`, B13 `app/db/supabase_client.py`) a tabuľka S1 v `supabase/migrations/`. Mimoriadna splátka (B6), úložisko (B12, `supabase_repository.py`) a endpointy FR-10, FR-11 zatiaľ chýbajú.

## Inštalácia (Windows, Python ≥ 3.12)

Z priečinka `backend/`:

```bash
python -m venv .venv
.venv/Scripts/python.exe -m pip install -r requirements-dev.txt
```

Ak `python` nie je v PATH, použite plnú cestu, napr. `%LOCALAPPDATA%\Programs\Python\Python313\python.exe`.

## Premenné prostredia

```bash
cp .env.example .env
```

Hodnoty `SUPABASE_URL` a `SUPABASE_SERVICE_ROLE_KEY` doplňte podľa časti „Nastavenie Supabase“ v `README.md` v koreni projektu. Testy `.env` nepotrebujú a k Supabase sa nepripájajú.

## Testy

```bash
.venv/Scripts/python.exe -m pytest
```

## Spustenie

```bash
.venv/Scripts/python.exe -m uvicorn app.main:app
```

- API: `http://127.0.0.1:8000/api/calculate`
- Dokumentácia OpenAPI: `http://127.0.0.1:8000/docs`

Príklad:

```bash
curl -X POST http://127.0.0.1:8000/api/calculate -H "Content-Type: application/json" -d "{\"amount\":\"100 000\",\"rate\":\"4\",\"years\":\"30\"}"
```

```json
{"status":"ok","results":{"monthly":"477,42 €","total":"171 869,51 €","interest":"71 869,51 €","extra":null}}
```
