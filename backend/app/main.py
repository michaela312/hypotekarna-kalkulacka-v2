"""B14 – vstupný bod aplikácie FastAPI.

Implementuje NFR-V2-08 (spustenie jedným príkazom), AD-V2-05 (backend servíruje frontend/)
a výber úložiska podľa B15 (STORAGE=supabase → B13, STORAGE=memory → InMemoryRepository).
Spustenie z priečinka backend/: uvicorn app.main:app
"""
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.routes import router
from app.config import Settings, load_settings
from app.db.repository import CalculationRepository, InMemoryRepository
from app.db.supabase_client import create_supabase_client
from app.db.supabase_repository import SupabaseRepository

FRONTEND_DIR = Path(__file__).resolve().parents[2] / 'frontend'


def build_repository(settings: Settings) -> CalculationRepository:
    if settings.storage == 'memory':
        return InMemoryRepository()
    return SupabaseRepository(create_supabase_client(settings))


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Pri chýbajúcej premennej (B15) vyhodí ConfigError a aplikácia sa nespustí.
    app.state.repository = build_repository(load_settings())
    yield


app = FastAPI(title='Hypotekárna kalkulačka V2', lifespan=lifespan)
app.include_router(router)

# StaticFiles sa pripája ako posledné, inak by '/' prekrylo '/api'.
if FRONTEND_DIR.is_dir():
    app.mount('/', StaticFiles(directory=FRONTEND_DIR, html=True), name='frontend')
