"""Testy NFR-V2-06 (kľúč Supabase nie je v gite) a S1 (migrácia tabuľky calculations)."""
import re
import subprocess
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]
ROOT = BACKEND.parent
MIGRATIONS = ROOT / 'supabase' / 'migrations'


def git(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(['git', *args], cwd=ROOT, capture_output=True, text=True)


def test_env_je_ignorovany_gitom():
    """NFR-V2-06: backend/.env je v .gitignore."""
    assert git('check-ignore', '-q', 'backend/.env').returncode == 0


def test_env_nie_je_v_repozitari():
    """NFR-V2-06: žiadny súbor .env nie je sledovaný gitom."""
    tracked = git('ls-files').stdout.splitlines()
    assert [f for f in tracked if Path(f).name == '.env'] == []


def test_env_example_bez_hodnot():
    """NFR-V2-06: .env.example obsahuje iba názvy premenných, nie URL ani kľúč."""
    lines = (BACKEND / '.env.example').read_text(encoding='utf-8').splitlines()
    values = dict(line.split('=', 1) for line in lines if line and not line.startswith('#'))
    assert values == {'STORAGE': 'supabase', 'SUPABASE_URL': '', 'SUPABASE_SERVICE_ROLE_KEY': ''}


def test_migracia_calculations():
    """S1, FR-10, FR-11, AD-V2-06: 17 stĺpcov, index podľa času a zapnuté RLS bez politík."""
    [migration] = MIGRATIONS.glob('*_create_calculations.sql')
    sql = migration.read_text(encoding='utf-8')
    body = re.search(r'create table public\.calculations \((.*?)\n\);', sql, re.S).group(1)
    columns = re.findall(r'^\s{2}([a-z_]+)\s+(?:uuid|timestamptz|numeric|smallint|text)', body, re.M)
    assert len(columns) == 17
    assert 'alter table public.calculations enable row level security;' in sql
    assert 'create policy' not in sql
    assert 'calculations (created_at desc)' in sql
