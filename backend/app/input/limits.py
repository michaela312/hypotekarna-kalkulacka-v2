"""B2 – hranice vstupov (V1: M2).

Implementuje IN-01 až IN-03 (hodnoty hraníc). Obsahuje iba dáta, žiadnu logiku.
"""
from dataclasses import dataclass
from typing import Literal

Field = Literal['amount', 'rate', 'years']


@dataclass(frozen=True)
class FieldLimits:
    min: int
    max: int
    decimals: int


LIMITS: dict[Field, FieldLimits] = {
    'amount': FieldLimits(min=1000, max=1_000_000, decimals=2),  # IN-01
    'rate': FieldLimits(min=0, max=20, decimals=2),              # IN-02
    'years': FieldLimits(min=1, max=30, decimals=0),             # IN-03
}
