"""B7 – slovenský formát čísel a súm (V1: M6).

Implementuje FR-04, FR-11 (sadzba) a DR-03 (zaokrúhlenie zobrazených výsledkov cez B5).
Formátuje sa ručne, nie cez locale, aby výstup mal obyčajné medzery U+0020 (AD-04 V1).
"""
import math
from decimal import Decimal

from app.domain.rounding import round_half_up


def format_number(value: float | Decimal, decimals: int) -> str:
    rounded = round_half_up(value, decimals)
    sign = '-' if rounded < 0 else ''
    whole, _, fraction = f'{abs(rounded):.{decimals}f}'.partition('.')
    groups = []
    while whole:
        groups.insert(0, whole[-3:])
        whole = whole[:-3]
    text = sign + ' '.join(groups)
    return f'{text},{fraction}' if decimals > 0 else text


def format_money(value: float | Decimal) -> str:
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError('Neplatná suma na formátovanie.')
    return f'{format_number(value, 2)} €'


def format_rate(value: float | Decimal) -> str:
    """FR-11: sadzba v tvare `4,00 %`."""
    return f'{format_number(value, 2)} %'
