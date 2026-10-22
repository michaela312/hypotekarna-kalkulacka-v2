"""B9 – orchestrácia jedného výpočtu (V1: M8).

Implementuje FR-01 až FR-09 (end-to-end), DR-04 a DR-10 (akceptačné testy na referenčných príkladoch)
a FR-10 (zaokrúhlené hodnoty na uloženie, AD-V2-08).
Poradie krokov podľa 02a-tiers.md, časť 3.2: B3 → B4 → (mimoriadna splátka) B4 balance_after → B5 round_down
→ B3 validate_extra_against_loan → B6 → B7, B8 → B5 (SavedValues).
Sám nič nepočíta, neformátuje ani nevaliduje. Neimportuje fastapi, pydantic ani app.db (NFR-V2-03).
"""
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Literal

from app.domain.extra_payment import ExtraParams, ExtraResultRaw, calculate_extra
from app.domain.mortgage import LoanParams, balance_after, calculate_mortgage
from app.domain.rounding import round_down, round_half_up
from app.format.money import format_money
from app.input.limits import BASE_FIELDS, LIMITS, Field
from app.input.validate import ErrorCode, Mode, RawInput, validate_extra_against_loan, validate_inputs
from app.text.messages import error_message, extra_amount_message, extra_month_message, payments_text


@dataclass(frozen=True)
class ExtraResult:
    # Hotové texty FR-06 až FR-08. Polia druhého režimu sú None.
    mode: Mode
    total: str
    interest: str
    interest_saved: str
    payments: str | None = None        # shorter_term, FR-06
    last_payment: str | None = None    # shorter_term, FR-06
    new_monthly: str | None = None     # lower_payment, FR-07


@dataclass(frozen=True)
class Results:
    monthly: str
    total: str
    interest: str
    extra: ExtraResult | None = None   # None = IN-04 aj IN-05 prázdne


@dataclass(frozen=True)
class CalculationResponse:
    # status 'ok' má iba results, status 'invalid' má iba errors (FR-05, FR-09).
    status: Literal['ok', 'invalid']
    results: Results | None = None
    errors: dict[Field, str] = field(default_factory=dict)


@dataclass(frozen=True)
class SavedExtra:
    # Časť SavedValues, zaokrúhlené na 0,01 € (AD-V2-08, OQ-V2-05).
    month: int                           # IN-04
    amount: Decimal                      # IN-05
    mode: Mode                           # IN-06
    total_paid: Decimal                  # FR-06, FR-07
    total_interest: Decimal              # FR-06, FR-07
    interest_saved: Decimal              # FR-08
    payments: int | None = None          # iba shorter_term (FR-06)
    last_payment: Decimal | None = None  # iba shorter_term (FR-06)
    new_monthly: Decimal | None = None   # iba lower_payment (FR-07)


@dataclass(frozen=True)
class SavedValues:
    # Platné vstupy a výsledky zaokrúhlené na 0,01 € (AD-V2-08).
    amount: Decimal                 # IN-01
    rate: Decimal                   # IN-02
    years: int                      # IN-03
    monthly_payment: Decimal        # FR-01
    total_paid: Decimal             # FR-02
    total_interest: Decimal         # FR-03
    extra: SavedExtra | None = None


@dataclass(frozen=True)
class CalculationOutcome:
    response: CalculationResponse
    values: SavedValues | None = None   # None pri neplatnom vstupe: neukladá sa nič


def _loan_params(values: dict[Field, Decimal]) -> LoanParams:
    return LoanParams(
        principal=float(values['amount']),
        annual_rate_pct=float(values['rate']),
        years=int(values['years']),
    )


def _messages(errors: dict[Field, ErrorCode], max_month: int, month: int | None,
              balance: Decimal | None) -> dict[Field, str]:
    messages: dict[Field, str] = {}
    for name, code in errors.items():
        if name == 'extra_month':
            messages[name] = extra_month_message(max_month)
        elif name == 'extra_amount':
            messages[name] = extra_amount_message(code, month, balance)
        else:
            messages[name] = error_message(name, code)
    return messages


def _validate(raw: RawInput) -> tuple[dict[Field, str], dict[Field, Decimal]]:
    """Kroky 1, 3, 4, 5 z 02a-tiers.md 3.2. Vráti (správy chýb, platné hodnoty)."""
    validation = validate_inputs(raw)
    errors = dict(validation.errors)
    partial = validation.partial
    base_valid = all(name in partial for name in BASE_FIELDS)
    # Ak je IN-03 neplatný, horná hranica IN-04 je n − 1 pre 30 rokov (FR-09).
    n = int(partial['years']) * 12 if 'years' in partial else LIMITS['years'].max * 12

    month = balance = None
    if validation.has_extra and base_valid and 'extra_month' in partial:
        month = int(partial['extra_month'])
        # Zostatok má zmysel iba pre K ≤ n − 1; inak B3 vráti chybu IN-04 a zostatok sa nepoužije.
        floor = round_down(balance_after(_loan_params(partial), month)) if month <= n - 1 else Decimal(0)
        loan_errors = validate_extra_against_loan(month, partial.get('extra_amount'), n, floor)
        errors.update(loan_errors)
        if 'extra_month' not in loan_errors:
            balance = floor     # IN-01 až IN-04 platné → správa IN-05 uvedie zostatok

    if errors:
        return _messages(errors, n - 1, month, balance), {}
    return {}, validation.values


def _extra_result(extra: ExtraResultRaw, mode: Mode, n: int) -> ExtraResult:
    common = dict(
        mode=mode,
        total=format_money(extra.total_paid),
        interest=format_money(extra.total_interest),
        interest_saved=format_money(extra.interest_saved),
    )
    if mode == 'shorter_term':
        return ExtraResult(**common, payments=payments_text(extra.payments, n),
                           last_payment=format_money(extra.last_payment))
    return ExtraResult(**common, new_monthly=format_money(extra.new_monthly))


def _round_optional(value: float | None) -> Decimal | None:
    return None if value is None else round_half_up(value)


def _saved_extra(extra: ExtraResultRaw, params: ExtraParams, amount: Decimal) -> SavedExtra:
    return SavedExtra(
        month=params.month, amount=round_half_up(amount), mode=params.mode,
        total_paid=round_half_up(extra.total_paid),
        total_interest=round_half_up(extra.total_interest),
        interest_saved=round_half_up(extra.interest_saved),
        payments=extra.payments,
        last_payment=_round_optional(extra.last_payment),
        new_monthly=_round_optional(extra.new_monthly),
    )


def run_calculation(raw: RawInput) -> CalculationOutcome:
    errors, values = _validate(raw)
    if errors:
        return CalculationOutcome(CalculationResponse(status='invalid', errors=errors))

    params = _loan_params(values)
    loan = calculate_mortgage(params)

    extra_result = saved_extra = None
    if 'extra_month' in values:
        extra_params = ExtraParams(month=int(values['extra_month']), amount=float(values['extra_amount']),
                                   mode=raw.mode)
        extra = calculate_extra(params, extra_params)
        extra_result = _extra_result(extra, raw.mode, params.years * 12)
        saved_extra = _saved_extra(extra, extra_params, values['extra_amount'])

    response = CalculationResponse(status='ok', results=Results(
        monthly=format_money(loan.monthly_payment),
        total=format_money(loan.total_paid),
        interest=format_money(loan.total_interest),
        extra=extra_result,
    ))
    saved = SavedValues(
        amount=round_half_up(values['amount']),
        rate=round_half_up(values['rate']),
        years=int(values['years']),
        monthly_payment=round_half_up(loan.monthly_payment),
        total_paid=round_half_up(loan.total_paid),
        total_interest=round_half_up(loan.total_interest),
        extra=saved_extra,
    )
    return CalculationOutcome(response, saved)
