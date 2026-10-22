"""B13 – úložisko výpočtov nad tabuľkou calculations v Supabase.

Implementuje FR-10, FR-11, NFR-V2-06 a NFR-V2-07: prevod SavedValues na riadok tabuľky S1 a späť;
každú chybu klienta Supabase alebo prekročenie času 4 s prevedie na StorageError.
"""
from datetime import datetime
from decimal import Decimal
from typing import Any

from supabase import Client

from app.db.repository import LIST_LIMIT, SavedRecord, StorageError
from app.db.supabase_client import TABLE
from app.services.calculator import SavedExtra, SavedValues

CENT = Decimal('0.01')
EXTRA_COLUMNS = ('extra_month', 'extra_amount', 'extra_mode', 'extra_payments', 'extra_last_payment',
                 'extra_new_monthly', 'extra_total_paid', 'extra_total_interest', 'extra_interest_saved')


def _text(value: Decimal | None) -> str | None:
    return None if value is None else str(value)


def _money(value: Any) -> Decimal | None:
    # PostgREST vracia numeric ako číslo JSON (napr. 477.42); str() zachová zápis bez binárnej chyby.
    return None if value is None else Decimal(str(value)).quantize(CENT)


def to_row(values: SavedValues) -> dict[str, str | int | None]:
    # Sumy idú ako text, nie float, aby sa nestratili centy. PostgreSQL ich prevedie na numeric.
    row: dict[str, str | int | None] = {
        'amount': str(values.amount),                    # IN-01
        'rate': str(values.rate),                        # IN-02
        'years': values.years,                           # IN-03
        'monthly_payment': str(values.monthly_payment),  # FR-01
        'total_paid': str(values.total_paid),            # FR-02
        'total_interest': str(values.total_interest),    # FR-03
    }
    extra = values.extra
    if extra is None:
        # Constraint extra_all_or_nothing: bez mimoriadnej splátky sú všetky stĺpce extra_* NULL.
        return row | dict.fromkeys(EXTRA_COLUMNS)
    return row | {
        'extra_month': extra.month,                                # IN-04
        'extra_amount': str(extra.amount),                         # IN-05
        'extra_mode': extra.mode,                                  # IN-06
        'extra_payments': extra.payments,                          # FR-06
        'extra_last_payment': _text(extra.last_payment),           # FR-06
        'extra_new_monthly': _text(extra.new_monthly),             # FR-07
        'extra_total_paid': str(extra.total_paid),                 # FR-06, FR-07
        'extra_total_interest': str(extra.total_interest),         # FR-06, FR-07
        'extra_interest_saved': str(extra.interest_saved),         # FR-08
    }


def from_row(row: dict[str, Any]) -> SavedRecord:
    extra = None
    if row['extra_month'] is not None:
        extra = SavedExtra(
            month=row['extra_month'], amount=_money(row['extra_amount']), mode=row['extra_mode'],
            payments=row['extra_payments'], last_payment=_money(row['extra_last_payment']),
            new_monthly=_money(row['extra_new_monthly']), total_paid=_money(row['extra_total_paid']),
            total_interest=_money(row['extra_total_interest']), interest_saved=_money(row['extra_interest_saved']),
        )
    values = SavedValues(
        amount=_money(row['amount']), rate=_money(row['rate']), years=row['years'],
        monthly_payment=_money(row['monthly_payment']), total_paid=_money(row['total_paid']),
        total_interest=_money(row['total_interest']), extra=extra,
    )
    return SavedRecord(id=row['id'], created_at=datetime.fromisoformat(row['created_at']), values=values)


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

    def list_latest(self, limit: int = LIST_LIMIT) -> list[SavedRecord]:
        try:
            # Bez opakovania: postgrest pri 5xx opakuje GET 3× s čakaním ~7 s, frontend čaká najviac 5 s
            # (API-R7) a NFR-V2-07 povoľuje 2 s. Opakovanie rieši používateľ, nie backend.
            response = (self._client.table(TABLE).select('*')
                        .order('created_at', desc=True).limit(limit).retry(False).execute())
            return [from_row(row) for row in response.data]
        except Exception as err:  # sieť, timeout, chyba PostgREST alebo neočakávaný tvar riadku
            raise StorageError(f'Uložené výpočty sa nepodarilo načítať zo Supabase: {err}') from err
