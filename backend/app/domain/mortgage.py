"""B4 – výpočet splátky a súčtov (V1: M4).

Implementuje FR-01, FR-02, FR-03, DR-01, DR-02, DR-03 (medzivýsledky sa nezaokrúhľujú) a DR-05 (zostatok).
Nič nezaokrúhľuje a nič nevaliduje okrem kontraktu (TQ-01).
"""
import math
from dataclasses import dataclass


@dataclass(frozen=True)
class LoanParams:
    principal: float
    annual_rate_pct: float
    years: int


@dataclass(frozen=True)
class LoanResult:
    monthly_payment: float
    total_paid: float
    total_interest: float


def annuity_payment(principal: float, monthly_rate: float, n: int) -> float:
    if monthly_rate > 0:
        return principal * monthly_rate / (1 - (1 + monthly_rate) ** -n)  # DR-01
    return principal / n                                                  # DR-02


def _check(params: LoanParams) -> None:
    values = (params.principal, params.annual_rate_pct, params.years)
    if (not all(math.isfinite(v) for v in values)
            or params.principal <= 0 or params.annual_rate_pct < 0 or params.years < 1):
        raise ValueError('Neplatné parametre úveru.')


def monthly_rate(params: LoanParams) -> float:
    return params.annual_rate_pct / 100 / 12


def calculate_mortgage(params: LoanParams) -> LoanResult:
    _check(params)
    i = monthly_rate(params)
    n = params.years * 12
    monthly = annuity_payment(params.principal, i, n)
    total = monthly * n                     # DR-03: s nezaokrúhleným M
    return LoanResult(monthly_payment=monthly, total_paid=total, total_interest=total - params.principal)


def balance_after(params: LoanParams, months: int) -> float:
    """DR-05: zostatok po splátke `months`. B_0 = P, B_j = B_(j−1) · (1 + i) − M. Nezaokrúhľuje sa (DR-03)."""
    _check(params)
    if months < 0:
        raise ValueError('Počet mesiacov nesmie byť záporný.')
    i = monthly_rate(params)
    payment = annuity_payment(params.principal, i, params.years * 12)
    balance = params.principal
    for _ in range(months):
        balance = balance * (1 + i) - payment
    return balance
