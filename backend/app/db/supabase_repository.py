"""B13 – úložisko výpočtov nad tabuľkou calculations v Supabase.

Implementuje FR-10, NFR-V2-06 a NFR-V2-07: každú chybu klienta Supabase alebo prekročenie času 4 s
prevedie na StorageError.
"""
from datetime import datetime

from supabase import Client

from app.db.repository import SavedRecord, StorageError
from app.db.supabase_client import TABLE
from app.services.calculator import SavedValues


def to_row(values: SavedValues) -> dict[str, str | int]:
    # Sumy idú ako text, nie float, aby sa nestratili centy. PostgreSQL ich prevedie na numeric.
    return {
        'amount': str(values.amount),                    # IN-01
        'rate': str(values.rate),                        # IN-02
        'years': values.years,                           # IN-03
        'monthly_payment': str(values.monthly_payment),  # FR-01
        'total_paid': str(values.total_paid),            # FR-02
        'total_interest': str(values.total_interest),    # FR-03
    }


class SupabaseRepository:
    def __init__(self, client: Client):
        self._client = client

    def save(self, values: SavedValues) -> SavedRecord:
        try:
            response = self._client.table(TABLE).insert(to_row(values)).execute()
            [row] = response.data
            return SavedRecord(id=row['id'], created_at=datetime.fromisoformat(row['created_at']), values=values)
        except Exception as err:  # sieť, timeout, chyba PostgREST alebo neočakávaná odpoveď
            raise StorageError(f'Výpočet sa nepodarilo uložiť do Supabase: {err}') from err
