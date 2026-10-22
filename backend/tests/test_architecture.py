"""Architektonické testy – NFR-V2-03 a pravidlá 1, 2 v Dependency Direction (docs/v2/02-architecture.md)."""
import ast
from pathlib import Path

import pytest

APP = Path(__file__).resolve().parents[1] / 'app'
CORE = ['input', 'domain', 'format', 'text', 'services']  # B1 až B9
FORBIDDEN = ('fastapi', 'pydantic', 'supabase', 'app.api', 'app.db')


def imports(path: Path) -> set[str]:
    names = set()
    for node in ast.walk(ast.parse(path.read_text(encoding='utf-8'))):
        if isinstance(node, ast.Import):
            names.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.add(node.module)
    return names


@pytest.mark.parametrize('path', [p for d in CORE for p in (APP / d).glob('*.py')], ids=lambda p: p.name)
def test_jadro_bez_frameworku(path):
    """NFR-V2-03: B1 až B9 neimportujú fastapi, pydantic, supabase, app.api ani app.db."""
    bad = {n for n in imports(path) if n.startswith(FORBIDDEN)}
    assert bad == set()


ALL = sorted(APP.rglob('*.py'))


@pytest.mark.parametrize('path', ALL, ids=lambda p: str(p.relative_to(APP)))
def test_supabase_a_prostredie_iba_v_povolenych_moduloch(path):
    """Pravidlo 4, NFR-V2-06: iba app/db/supabase_*.py importuje supabase, iba B15 číta prostredie."""
    names = imports(path)
    if not (path.parent.name == 'db' and path.name.startswith('supabase_')):
        assert not any(n == 'supabase' or n.startswith('supabase.') for n in names)
    if path.name != 'config.py':
        assert not {'os', 'dotenv'} & names
        assert 'environ' not in path.read_text(encoding='utf-8')


@pytest.mark.parametrize('path', ['input/parse.py', 'input/limits.py', 'domain/mortgage.py', 'domain/rounding.py'])
def test_zakladne_moduly_bez_importov_aplikacie(path):
    """Pravidlo 2: B1, B2, B4 a B5 neimportujú žiadny modul aplikácie."""
    assert {n for n in imports(APP / path) if n.startswith('app')} == set()


def test_b6_importuje_iba_b4():
    """Pravidlo 2: B6 (extra_payment.py) importuje z aplikácie iba B4 (mortgage.py)."""
    assert {n for n in imports(APP / 'domain/extra_payment.py') if n.startswith('app')} == {'app.domain.mortgage'}
