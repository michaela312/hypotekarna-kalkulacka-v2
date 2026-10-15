"""B4 – výpočet splátky a súčtov (V1: M4).

Implementuje FR-01, FR-02, FR-03, DR-01, DR-02 a DR-03 (medzivýsledky sa nezaokrúhľujú).
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


def calculate_mortgage(params: LoanParams) -> LoanResult:
    values = (params.principal, params.annual_rate_pct, params.years)
    if (not all(math.isfinite(v) for v in values)
            or params.principal <= 0 or params.annual_rate_pct < 0 or params.years < 1):
        raise ValueError('Neplatné parametre úveru.')

    i = params.annual_rate_pct / 100 / 12
    n = params.years * 12
    monthly = annuity_payment(params.principal, i, n)
    total = monthly * n                     # DR-03: s nezaokrúhleným M
    return LoanResult(monthly_payment=monthly, total_paid=total, total_interest=total - params.principal)
