"""B6 – mimoriadna splátka (NOVÉ vo V2).

Implementuje FR-06, FR-07, FR-08 a DR-05 až DR-09: nezaokrúhlený priebeh úveru po jednej mimoriadnej
splátke E v mesiaci K. Importuje iba B4. Nezaokrúhľuje (DR-03) a nevaliduje (to robí B3).
"""
from dataclasses import dataclass
from typing import Literal

from app.domain.mortgage import LoanParams, annuity_payment, balance_after, calculate_mortgage, monthly_rate

Mode = Literal['shorter_term', 'lower_payment']

# Zostatok ≤ 1e-6 € sa považuje za splatený, rovnako ako prah v B5 (DR-07).
_ZERO_THRESHOLD = 1e-6


@dataclass(frozen=True)
class ExtraParams:
    month: int        # K (IN-04), 1 ≤ K ≤ n − 1
    amount: float     # E (IN-05), 0 < E < B_K
    mode: Mode        # IN-06


@dataclass(frozen=True)
class ExtraResultRaw:
    total_paid: float               # DR-09
    total_interest: float           # DR-09
    interest_saved: float           # FR-08
    payments: int | None = None     # shorter_term: K + m (DR-07)
    last_payment: float | None = None
    new_monthly: float | None = None  # lower_payment: M' (DR-08)


def _shorter_term(balance: float, i: float, payment: float, max_payments: int) -> tuple[int, float, float]:
    """DR-07: splátka M sa nemení. Vráti (m, súčet splátok po K, posledná splátka).

    Cyklus má najviac `max_payments` = n − K krokov: pri E > 0 sa úver nemôže splácať dlhšie ako bez neho.
    Posledný povolený krok zaplatí celý zostatok, aby chyba floatu nepridala splátku navyše (R-P-02).
    """
    paid = 0.0
    for m in range(1, max_payments + 1):
        due = balance * (1 + i)
        if due <= payment or m == max_payments:
            return m, paid + due, due
        balance = due - payment
        paid += payment
        if balance <= _ZERO_THRESHOLD:
            return m, paid, payment
    raise ValueError('Mimoriadna splátka v mesiaci n alebo neskôr nie je možná.')


def calculate_extra(params: LoanParams, extra: ExtraParams) -> ExtraResultRaw:
    n = params.years * 12
    k = extra.month
    if not 1 <= k <= n - 1 or extra.amount <= 0:
        raise ValueError('Neplatné parametre mimoriadnej splátky.')   # kontrakt (TQ-01)

    base = calculate_mortgage(params)
    i = monthly_rate(params)
    payment = base.monthly_payment
    remaining = balance_after(params, k) - extra.amount               # DR-06: B'_K = B_K − E
    if remaining <= 0:
        raise ValueError('Mimoriadna splátka musí byť menšia ako zostatok úveru.')

    paid_until_k = k * payment + extra.amount                         # DR-09: K · M + E
    if extra.mode == 'shorter_term':
        m, paid_after, last = _shorter_term(remaining, i, payment, n - k)
        total = paid_until_k + paid_after
        result = dict(payments=k + m, last_payment=last)
    else:
        new_monthly = annuity_payment(remaining, i, n - k)             # DR-08, pri 0 % B'_K / (n − K)
        total = paid_until_k + new_monthly * (n - k)
        result = dict(new_monthly=new_monthly)

    interest = total - params.principal
    return ExtraResultRaw(
        total_paid=total,
        total_interest=interest,
        interest_saved=base.total_interest - interest,                # FR-08: oba nezaokrúhlené
        **result,
    )
