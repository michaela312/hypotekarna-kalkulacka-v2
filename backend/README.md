# Backend V2 (Python, FastAPI)

Implementuje FR-01 až FR-05 V2 cez `POST /api/calculate` podľa `docs/v2/api-contract.md`.
Moduly B1–B5, B7–B11 a B14 podľa `docs/v2/02-architecture.md`. Mimoriadna splátka (B6) a Supabase (B12, B13, S1) zatiaľ chýbajú.

## Inštalácia (Windows, Python ≥ 3.12)

Z priečinka `backend/`:

```bash
python -m venv .venv
.venv/Scripts/python.exe -m pip install -r requirements-dev.txt
```

Ak `python` nie je v PATH, použite plnú cestu, napr. `%LOCALAPPDATA%\Programs\Python\Python313\python.exe`.

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
