"""B5 – zaokrúhľovanie (V1: M5).

Implementuje DR-03: matematické zaokrúhlenie (polovica nahor) iba zobrazených výsledkov,
a IN-05: zostatok zaokrúhlený nadol ako horná hranica mimoriadnej splátky.
"""
import math
from decimal import ROUND_FLOOR, ROUND_HALF_UP, Decimal

# Zvyšky binárnej aritmetiky (napr. M × n − P = ±1.1e-13 pri sadzbe 0 %) sa považujú za 0.
_ZERO_THRESHOLD = 1e-6


def _to_decimal(value: float | int | Decimal) -> Decimal:
    # repr() dáva najkratší zápis floatu ako JavaScript vo V1, takže 1.005 → "1.005" → 1.01.
    if isinstance(value, int):
        value = Decimal(value)
    elif isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError('Neplatné číslo na zaokrúhlenie.')
        if abs(value) < _ZERO_THRESHOLD:
            value = 0.0
        value = Decimal(repr(value))
    elif not value.is_finite():
        raise ValueError('Neplatné číslo na zaokrúhlenie.')
    return value


def _quantize(value: Decimal, decimals: int, rounding: str) -> Decimal:
    result = value.quantize(Decimal(1).scaleb(-decimals), rounding=rounding)
    return result.copy_abs() if result.is_zero() else result  # nikdy nie -0


def round_half_up(value: float | int | Decimal, decimals: int = 2) -> Decimal:
    # Python round() zaokrúhľuje na párne číslo (round(0.125, 2) == 0.12), preto sa nepoužíva (AD-V2-10).
    return _quantize(_to_decimal(value), decimals, ROUND_HALF_UP)


def round_down(value: float | int | Decimal, decimals: int = 2) -> Decimal:
    """IN-05: zaokrúhlenie nadol (k −∞). 98 238,9636 → 98 238,96."""
    return _quantize(_to_decimal(value), decimals, ROUND_FLOOR)
