"""B9 – orchestrácia jedného výpočtu (V1: M8).

Implementuje FR-01 až FR-05 (end-to-end) a DR-04 (akceptačné testy na referenčných príkladoch).
Sám nič nepočíta, neformátuje ani nevaliduje. Neimportuje fastapi ani pydantic (NFR-V2-03).
"""
from dataclasses import dataclass, field
from typing import Literal

from app.domain.mortgage import LoanParams, calculate_mortgage
from app.format.money import format_money
from app.input.limits import Field
from app.input.validate import RawInput, validate_inputs
from app.text.messages import error_message


@dataclass(frozen=True)
class Results:
    monthly: str
    total: str
    interest: str


@dataclass(frozen=True)
class CalculationResponse:
    # status 'ok' má iba results, status 'invalid' má iba errors (FR-05).
    status: Literal['ok', 'invalid']
    results: Results | None = None
    errors: dict[Field, str] = field(default_factory=dict)


def run_calculation(raw: RawInput) -> CalculationResponse:
    validation = validate_inputs(raw)
    if not validation.valid:
        errors = {name: error_message(name, code) for name, code in validation.errors.items()}
        return CalculationResponse(status='invalid', errors=errors)

    values = validation.values
    loan = calculate_mortgage(LoanParams(
        principal=float(values['amount']),
        annual_rate_pct=float(values['rate']),
        years=int(values['years']),
    ))
    return CalculationResponse(status='ok', results=Results(
        monthly=format_money(loan.monthly_payment),
        total=format_money(loan.total_paid),
        interest=format_money(loan.total_interest),
    ))
