"""B3 – validácia vstupov (V1: M3).

Implementuje IN-01 až IN-06, FR-05 a FR-09 (zistenie neplatného vstupu). Nevytvára texty správ.
Neimportuje doménu: zostatok úveru dostane `validate_extra_against_loan` ako argument.
"""
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Literal

from app.input.limits import BASE_FIELDS, EXTRA_FIELDS, LIMITS, Field
from app.input.parse import parse_number

# no_room: zostatok v mesiaci K zaokrúhlený nadol je ≤ minimum IN-05, mimoriadna splátka nie je možná (FR-09).
ErrorCode = Literal['empty', 'nan', 'step', 'range', 'no_room']
Mode = Literal['shorter_term', 'lower_payment']


@dataclass(frozen=True)
class RawInput:
    amount: str
    rate: str
    years: str
    extra_month: str = ''                # IN-04
    extra_amount: str = ''               # IN-05
    mode: Mode = 'shorter_term'          # IN-06, predvolené podľa OQ-V2-03


@dataclass(frozen=True)
class ValidationResult:
    valid: bool
    values: dict[Field, Decimal] = field(default_factory=dict)
    errors: dict[Field, ErrorCode] = field(default_factory=dict)
    has_extra: bool = False              # False = IN-04 aj IN-05 prázdne, mimoriadna splátka sa nepočíta
    # Platné polia aj pri chybe v inom poli. B9 z nich zistí zostatok pre správu IN-05 (FR-09).
    partial: dict[Field, Decimal] = field(default_factory=dict)


def _check(raw: str, name: Field) -> Decimal | ErrorCode:
    # Poradie podmienok: prázdne → nie je číslo → priveľa desatinných miest → mimo rozsahu.
    parsed = parse_number(raw)
    if not parsed.ok:
        return parsed.reason
    limits = LIMITS[name]
    if parsed.decimals > limits.decimals:
        return 'step'
    if not limits.min <= parsed.value <= limits.max:
        return 'range'
    return parsed.value


def validate_inputs(raw: RawInput) -> ValidationResult:
    # Validujú sa všetky polia naraz, aby sa zobrazili všetky chyby (FR-05, príklad 3).
    # IN-04 a IN-05 sú voliteľné ako dvojica: obe prázdne = bez mimoriadnej splátky, nie chyba (FR-09).
    has_extra = any(getattr(raw, name).strip() for name in EXTRA_FIELDS)
    names = BASE_FIELDS + EXTRA_FIELDS if has_extra else BASE_FIELDS

    values: dict[Field, Decimal] = {}
    errors: dict[Field, ErrorCode] = {}
    for name in names:
        result = _check(getattr(raw, name), name)
        if isinstance(result, Decimal):
            values[name] = result
        else:
            errors[name] = result

    if errors:
        # FR-05, FR-09: pri chybe sa nevracajú hodnoty na výpočet.
        return ValidationResult(valid=False, errors=errors, has_extra=has_extra, partial=values)
    return ValidationResult(valid=True, values=values, has_extra=has_extra, partial=values)


def validate_extra_against_loan(
    month: int, amount: Decimal | None, n: int, balance_floor: Decimal,
) -> dict[Field, ErrorCode]:
    """Hranice IN-04 a IN-05 závislé od úveru (FR-09).

    month: staticky platný K; amount: staticky platné E, alebo None, ak E má statickú chybu;
    n: počet splátok; balance_floor: zostatok B_K zaokrúhlený nadol na 0,01 € (B5 round_down).
    """
    if month > n - 1:
        return {'extra_month': 'range'}                    # IN-04: K ≤ n − 1
    if balance_floor <= LIMITS['extra_amount'].min:
        return {'extra_amount': 'no_room'}                 # zostatok ≤ 100 € – žiadna suma nie je platná
    if amount is not None and amount >= balance_floor:
        return {'extra_amount': 'range'}                   # IN-05: E < zostatok
    return {}
