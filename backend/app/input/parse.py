"""B1 – prevod textu na číslo (V1: M1).

Implementuje IN-01 až IN-03 (pravidlá zápisu čísla) a FR-05 (podmienky „je prázdny“ a „nie je číslo“).
"""
import re
from dataclasses import dataclass
from decimal import Decimal
from typing import Literal

# Prijme iba tvar -?číslice[,|.číslice]. Napr. "1e3", "0x10" alebo "1,2,3" nie je číslo.
_NUMBER = re.compile(r'-?([0-9]+)(?:[.,]([0-9]+))?')

# Medzery medzi číslicami: obyčajná a nezalomiteľné (U+00A0, U+202F), ktoré vkladá formát sk-SK pri kopírovaní.
_SPACES = re.compile('[   ]')


@dataclass(frozen=True)
class ParsedNumber:
    ok: bool
    value: Decimal | None = None
    decimals: int = 0
    reason: Literal['empty', 'nan'] | None = None


def parse_number(raw: str) -> ParsedNumber:
    text = _SPACES.sub('', raw.strip())
    if text == '':
        return ParsedNumber(ok=False, reason='empty')

    match = _NUMBER.fullmatch(text)
    if match is None:
        return ParsedNumber(ok=False, reason='nan')

    fraction = match.group(2) or ''
    return ParsedNumber(ok=True, value=Decimal(text.replace(',', '.')), decimals=len(fraction))
