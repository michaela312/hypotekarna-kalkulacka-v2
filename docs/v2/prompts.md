# Prompty V2

## 01 a 02 – Prechod na 4 časti (frontend, API, backend, Supabase)

> Pozri si moju aktuálnu Hypotekárnu kalkulačku v tomto priečinku. Chcem ju prerobiť na architektúru so 4 časťami:
> 1. Frontend (HTML + JavaScript) – iba vstupy od používateľa a zobrazenie výsledku, volá API.
> 2. API – dohoda medzi frontendom a backendom (aký vstup, aký výstup).
> 3. Backend (Python, FastAPI) – všetky výpočty: mesačná splátka, mimoriadna splátka.
> 4. Supabase – databáza na ukladanie výpočtov.
> Zatiaľ nepíš kód. Navrhni štruktúru priečinkov (frontend/, backend/, docs/) a vypíš, ktoré časti súčasného kódu kam presunieme. Vysvetli mi to jednoducho.

> ano

(Odpoveď na otázku, či spísať návrh do `docs/v2/02-architecture.md` a začať `docs/v2/01-functional.md` s požiadavkami na mimoriadnu splátku.)

## 01-architecture-v2 – Implementačný pohľad po 4 vrstvách

> We are moving to a 4-tier architecture for the mortgage calculator. Create a new document docs/v2/01-architecture-v2.md detailing:
> 1. Frontend (JavaScript): handling inputs, UI rendering, fetching from API.
> 2. API Contract: JSON request/response structure between frontend and backend.
> 3. Backend (Python): FastAPI or lightweight service performing the mortgage and extra payment calculations.
> 4. Supabase: Database schema (tables for calculations, user history, or inputs) and connection setup.
> Keep it structured and ready for implementation.

## Backend – 1. časť (B1–B5, B7–B11, B14)

> Implement the Python backend service for the mortgage calculator.
> 1. Create a backend/ folder with a Python project structure (e.g., FastAPI app or module).
> 2. Move the exact annuity and payment calculation logic from our previous JavaScript implementation into Python.
> 3. Write unit tests in Python to verify that calculations (including 0% interest and rounding) match our reference values.
> 4. Expose an endpoint (e.g., POST /calculate) that accepts loan parameters and returns the monthly payment, total amount, and interest.

## Supabase – schéma a pripojenie

> Prepare the Supabase integration and database schema:
> 1. Create a supabase/ folder with migration SQL files (e.g., schema.sql) defining a calculations table to store loan parameters, results, and timestamps.
> 2. Add a configuration / client helper file in the project for connecting to Supabase.
> 3. Update the README with instructions on how to set up environment variables (Supabase URL and API keys).
