"""B3 – validácia vstupov (V1: M3).

Implementuje IN-01 až IN-03 a FR-05 (zistenie neplatného vstupu). Nevytvára texty správ.
"""
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Literal

from app.input.limits import LIMITS, Field
from app.input.parse import parse_number

ErrorCode = Literal['empty', 'nan', 'step', 'range']


@dataclass(frozen=True)
class RawInput:
    amount: str
    rate: str
    years: str


@dataclass(frozen=True)
class ValidationResult:
    valid: bool
    values: dict[Field, Decimal] = field(default_factory=dict)
    errors: dict[Field, ErrorCode] = field(default_factory=dict)


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
    values: dict[Field, Decimal] = {}
    errors: dict[Field, ErrorCode] = {}
    for name in LIMITS:
        result = _check(getattr(raw, name), name)
        if isinstance(result, Decimal):
            values[name] = result
        else:
            errors[name] = result

    if errors:
        return ValidationResult(valid=False, errors=errors)
    return ValidationResult(valid=True, values=values)
