"""B8 – texty pre používateľa (V1: M7).

Implementuje FR-05 a FR-09 (chybové správy s povoleným rozsahom), FR-06 (text počtu splátok)
a FR-11 (doba splácania a mimoriadna splátka v zozname, tvary slov podľa čísla).
"""
from decimal import Decimal
from typing import Literal

from app.format.money import format_money, format_number
from app.input.limits import LIMITS, BaseField
from app.input.validate import ErrorCode, Mode

_TEMPLATES: dict[BaseField, str] = {
    'amount': 'Výška úveru musí byť od {min} do {max} €.',
    'rate': 'Ročná úroková sadzba musí byť od {min} do {max} %.',
    'years': 'Doba splácania musí byť od {min} do {max} rokov.',
}

# Tvary podľa čísla: 1 → [0], 2 až 4 → [1], 0 a 5 a viac → [2].
_FORMS = {'mesiac': ('mesiac', 'mesiace', 'mesiacov'), 'rok': ('rok', 'roky', 'rokov')}

_MODE_TEXT: dict[Mode, str] = {'shorter_term': 'kratšia doba', 'lower_payment': 'nižšia splátka'}


def _n(value: int | Decimal) -> str:
    return format_number(value, 0)


def plural(count: int, word: Literal['mesiac', 'rok']) -> str:
    """Slovenský tvar slova podľa čísla (FR-06, FR-11)."""
    one, few, many = _FORMS[word]
    if count == 1:
        return one
    return few if 2 <= count <= 4 else many


def error_message(field: BaseField, code: ErrorCode) -> str:
    """FR-05: správa pre IN-01 až IN-03. Pre všetky kódy chýb jedného poľa je rovnaká."""
    limits = LIMITS[field]
    return _TEMPLATES[field].format(min=_n(limits.min), max=_n(limits.max))


def extra_month_message(max_month: int) -> str:
    """FR-09: správa pre IN-04. max_month = n − 1, pri neplatnom IN-03 359."""
    return f'Mesiac mimoriadnej splátky musí byť od {_n(LIMITS["extra_month"].min)} do {_n(max_month)}.'


def extra_amount_message(code: ErrorCode, month: int | None = None, balance: Decimal | None = None) -> str:
    """FR-09: správa pre IN-05.

    balance = zostatok B_K zaokrúhlený nadol, ak sú IN-01 až IN-04 platné; inak None.
    """
    limits = LIMITS['extra_amount']
    if code == 'no_room':
        return (f'V mesiaci {month} je zostatok úveru {format_money(balance)}, '
                f'mimoriadna splátka (min. {_n(limits.min)} €) nie je možná.')
    if balance is not None:
        return f'Mimoriadna splátka musí byť od {_n(limits.min)} € a menej ako zostatok úveru {format_money(balance)}.'
    return f'Mimoriadna splátka musí byť od {_n(limits.min)} do {_n(limits.max)} €.'


def payments_text(payments: int, n: int) -> str:
    """FR-06: `300 mesiacov (o 60 mesiacov menej)`."""
    fewer = n - payments
    return f'{payments} {plural(payments, "mesiac")} (o {fewer} {plural(fewer, "mesiac")} menej)'


def years_text(years: int) -> str:
    """FR-11: `30 rokov`."""
    return f'{years} {plural(years, "rok")}'


def extra_text(amount: Decimal, month: int, mode: Mode) -> str:
    """FR-11: `10 000,00 € v 12. mesiaci, kratšia doba`."""
    return f'{format_money(amount)} v {month}. mesiaci, {_MODE_TEXT[mode]}'
