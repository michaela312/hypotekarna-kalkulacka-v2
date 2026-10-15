"""B9 – orchestrácia jedného výpočtu (V1: M8).

Implementuje FR-01 až FR-05 (end-to-end), DR-04 (akceptačné testy na referenčných príkladoch)
a FR-10 (zaokrúhlené hodnoty na uloženie, AD-V2-08).
Sám nič nepočíta, neformátuje ani nevaliduje. Neimportuje fastapi, pydantic ani app.db (NFR-V2-03).
"""
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Literal

from app.domain.mortgage import LoanParams, calculate_mortgage
from app.domain.rounding import round_half_up
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


@dataclass(frozen=True)
class SavedValues:
    # Platné vstupy a výsledky zaokrúhlené na 0,01 € (AD-V2-08). Mimoriadna splátka pribudne s B6.
    amount: Decimal                 # IN-01
    rate: Decimal                   # IN-02
    years: int                      # IN-03
    monthly_payment: Decimal        # FR-01
    total_paid: Decimal             # FR-02
    total_interest: Decimal         # FR-03


@dataclass(frozen=True)
class CalculationOutcome:
    response: CalculationResponse
    values: SavedValues | None = None   # None pri neplatnom vstupe: neukladá sa nič


def run_calculation(raw: RawInput) -> CalculationOutcome:
    validation = validate_inputs(raw)
    if not validation.valid:
        errors = {name: error_message(name, code) for name, code in validation.errors.items()}
        return CalculationOutcome(CalculationResponse(status='invalid', errors=errors))

    values = validation.values
    loan = calculate_mortgage(LoanParams(
        principal=float(values['amount']),
        annual_rate_pct=float(values['rate']),
        years=int(values['years']),
    ))
    response = CalculationResponse(status='ok', results=Results(
        monthly=format_money(loan.monthly_payment),
        total=format_money(loan.total_paid),
        interest=format_money(loan.total_interest),
    ))
    saved = SavedValues(
        amount=round_half_up(values['amount']),
        rate=round_half_up(values['rate']),
        years=int(values['years']),
        monthly_payment=round_half_up(loan.monthly_payment),
        total_paid=round_half_up(loan.total_paid),
        total_interest=round_half_up(loan.total_interest),
    )
    return CalculationOutcome(response, saved)
