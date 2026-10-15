"""Spoločné fixtúry. Žiadny test sa nepripája na skutočnú Supabase (AD-V2-09)."""
import pytest

from app.api.routes import get_repository
from app.db.repository import InMemoryRepository
from app.main import app


@pytest.fixture(autouse=True)
def repository():
    """Každý test dostane prázdne pamäťové úložisko namiesto Supabase."""
    repo = InMemoryRepository()
    app.dependency_overrides[get_repository] = lambda: repo
    yield repo
    app.dependency_overrides.clear()
