"""B15 – nastavenia z premenných prostredia a súboru backend/.env.

Implementuje NFR-V2-06 (kľúč Supabase iba v backend/.env). Iba tento modul číta premenné prostredia.
"""
import os
from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv

ENV_FILE = Path(__file__).resolve().parents[1] / '.env'

Storage = Literal['supabase', 'memory']


class ConfigError(Exception):
    """Chýbajúca alebo neplatná premenná prostredia. Správa obsahuje jej názov."""


@dataclass(frozen=True)
class Settings:
    storage: Storage
    supabase_url: str | None = None
    # repr=False: kľúč sa nevypíše v logoch ani v chybových hláseniach.
    supabase_service_role_key: str | None = field(default=None, repr=False)


def load_settings(environ: Mapping[str, str] | None = None) -> Settings:
    if environ is None:
        load_dotenv(ENV_FILE)  # premenné, ktoré už sú nastavené v prostredí, sa neprepíšu
        environ = os.environ

    storage = environ.get('STORAGE', '').strip() or 'supabase'
    if storage not in ('supabase', 'memory'):
        raise ConfigError(f"STORAGE musí byť 'supabase' alebo 'memory', nie '{storage}'.")
    if storage == 'memory':
        return Settings(storage='memory')

    url = environ.get('SUPABASE_URL', '').strip()
    key = environ.get('SUPABASE_SERVICE_ROLE_KEY', '').strip()
    missing = [name for name, value in (('SUPABASE_URL', url), ('SUPABASE_SERVICE_ROLE_KEY', key)) if not value]
    if missing:
        raise ConfigError(f"Chýba premenná prostredia: {', '.join(missing)}. Pozri backend/.env.example.")
    if not url.startswith('https://'):
        raise ConfigError('SUPABASE_URL musí začínať https:// (napr. https://<projekt>.supabase.co).')

    return Settings(storage='supabase', supabase_url=url, supabase_service_role_key=key)
