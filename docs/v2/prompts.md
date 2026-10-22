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

## Frontend – 1. časť

> I want to create the Frontend (JavaScript + HTML) for the mortgage calculator to complete our 4-tier architecture. Before writing any code, please ask me a few quick questions about how I want it structured (e.g., simple single HTML file, styling preferences, or how it should handle errors), and then wait for my answers.

Odpovede na 4 otázky: štruktúra – jeden HTML súbor; vzhľad – čistý, minimalistický; výpočet a chyby – živý výpočet a správa pri nedostupnom backende; rozsah – iba základný výpočet.

## Supabase – ukladanie každého výpočtu

> Please fully integrate Supabase into our mortgage calculator backend so that data is actually stored in the database:
> 1. Update the calculation endpoint (POST /api/calculate) so that every valid calculation is automatically saved into our Supabase 'calculations' table using our backend helper.
> 2. If we have environment variables or a local .env setup, make sure the backend correctly reads them and handles database operations.
> 3. Write automated unit/integration tests for the database saving logic (mocking the Supabase response so tests pass reliably without needing a live internet connection).
> 4. Run the entire test suite, commit the changes to git, push to main, and update docs/handoff.md.

## Implementačný plán (05)

> I need a comprehensive, step-by-step implementation plan for refactoring and updating our Mortgage Calculator (Hypotekárna kalkulačka) application. We need to decouple the application into a clean 4-tier architecture, where each part has a single, well-defined responsibility: Frontend (JavaScript) – vstupy od používateľa a zobrazenie výsledku; volá API. API – dohoda medzi frontendom a backendom: aký vstup, aký výstup. Backend (Python) – výpočty: splátka, mimoriadna splátka, neskôr ďalšia logika. Supabase – databáza, do ktorej aplikácia ukladá dáta.

Výsledok: `docs/v2/05-plan.md`.
