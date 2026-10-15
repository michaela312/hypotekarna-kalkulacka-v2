"""B14 – vstupný bod aplikácie FastAPI.

Implementuje NFR-V2-08 (spustenie jedným príkazom) a AD-V2-05 (backend servíruje frontend/).
Spustenie z priečinka backend/: uvicorn app.main:app
"""
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.routes import router

FRONTEND_DIR = Path(__file__).resolve().parents[2] / 'frontend'

app = FastAPI(title='Hypotekárna kalkulačka V2')
app.include_router(router)

# StaticFiles sa pripája ako posledné, inak by '/' prekrylo '/api'. Frontend zatiaľ nemusí existovať.
if FRONTEND_DIR.is_dir():
    app.mount('/', StaticFiles(directory=FRONTEND_DIR, html=True), name='frontend')
