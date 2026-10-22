# Backend V2 (Python, FastAPI)

Implementuje FR-01 až FR-11 V2 podľa `docs/v2/api-contract.md`: výpočet a mimoriadna splátka cez `POST /api/calculate`, uloženie cez `POST /api/calculations` (iba po kliknutí, AD-V2-15) a zoznam 20 posledných cez `GET /api/calculations`.
Moduly B1–B15 podľa `docs/v2/02-architecture.md`. Úložisko: B12 `app/db/repository.py` (rozhranie a pamäťová implementácia), B13 `app/db/supabase_repository.py` (Supabase).

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

Hodnoty `SUPABASE_URL` a `SUPABASE_SERVICE_ROLE_KEY` doplňte podľa časti „Nastavenie Supabase“ v `README.md` v koreni projektu. Testy `.env` nepotrebujú a k Supabase sa nepripájajú: úložisko nahradí `InMemoryRepository` (`tests/conftest.py`) a HTTP odpovede Supabase simuluje `httpx.MockTransport` (`tests/db/test_supabase_repository.py`). Bez Supabase: `STORAGE=memory`.

## Testy

```bash
.venv/Scripts/python.exe -m pytest
```

## Spustenie

```bash
.venv/Scripts/python.exe -m uvicorn app.main:app
```

- API: `POST /api/calculate`, `POST /api/calculations`, `GET /api/calculations`, `GET /api/health`
- Dokumentácia OpenAPI: `http://127.0.0.1:8000/docs`

Príklad:

```bash
curl -X POST http://127.0.0.1:8000/api/calculate -H "Content-Type: application/json" -d "{\"amount\":\"100 000\",\"rate\":\"4\",\"years\":\"30\",\"extra\":{\"month\":\"\",\"amount\":\"\",\"mode\":\"shorter_term\"}}"
```

```json
{"status":"ok","results":{"monthly":"477,42 €","total":"171 869,51 €","interest":"71 869,51 €","extra":null}}
```
