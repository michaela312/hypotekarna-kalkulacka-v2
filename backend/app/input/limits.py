"""B2 – hranice vstupov (V1: M2).

Implementuje IN-01 až IN-05 (statické hranice). Obsahuje iba dáta, žiadnu logiku.
Hranice závislé od úveru (n − 1 pre IN-04, zostatok B_K pre IN-05) tu nie sú, overuje ich B3
`validate_extra_against_loan` s hodnotami, ktoré vypočíta B9.
"""
from dataclasses import dataclass
from typing import Literal

Field = Literal['amount', 'rate', 'years', 'extra_month', 'extra_amount']
BaseField = Literal['amount', 'rate', 'years']


@dataclass(frozen=True)
class FieldLimits:
    min: int
    max: int
    decimals: int


LIMITS: dict[Field, FieldLimits] = {
    'amount': FieldLimits(min=1000, max=1_000_000, decimals=2),      # IN-01
    'rate': FieldLimits(min=0, max=20, decimals=2),                  # IN-02
    'years': FieldLimits(min=1, max=30, decimals=0),                 # IN-03
    'extra_month': FieldLimits(min=1, max=359, decimals=0),          # IN-04, max = n − 1 pri 30 rokoch
    'extra_amount': FieldLimits(min=100, max=1_000_000, decimals=2), # IN-05
}

BASE_FIELDS: tuple[BaseField, ...] = ('amount', 'rate', 'years')
EXTRA_FIELDS: tuple[Field, ...] = ('extra_month', 'extra_amount')
