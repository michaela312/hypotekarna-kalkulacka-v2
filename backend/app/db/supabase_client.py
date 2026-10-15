"""B13 (časť) – pripojenie k Supabase.

Implementuje NFR-V2-06 (kľúč service_role iba v backende, AD-V2-06) a NFR-V2-07 (čakanie najviac 4 s).
Iba moduly app/db/supabase_*.py importujú balík supabase (pravidlo 4 v Dependency Direction).
"""
from supabase import Client, ClientOptions, create_client

from app.config import Settings

TABLE = 'calculations'      # S1, supabase/migrations/
TIMEOUT_SECONDS = 4         # NFR-V2-07


def create_supabase_client(settings: Settings) -> Client:
    if settings.storage != 'supabase':
        raise ValueError("Klient Supabase sa vytvára iba pri STORAGE=supabase.")
    options = ClientOptions(
        postgrest_client_timeout=TIMEOUT_SECONDS,
        # Backend sa neprihlasuje ako používateľ, takže reláciu netreba ukladať ani obnovovať.
        persist_session=False,
        auto_refresh_token=False,
    )
    return create_client(settings.supabase_url, settings.supabase_service_role_key, options=options)
