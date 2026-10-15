"""B8 – chybové správy (V1: M7).

Implementuje FR-05 (obsah chybovej správy s povoleným rozsahom).
Pre všetky kódy chýb jedného poľa vráti tú istú správu.
"""
from app.format.money import format_number
from app.input.limits import LIMITS, Field
from app.input.validate import ErrorCode

_TEMPLATES: dict[Field, str] = {
    'amount': 'Výška úveru musí byť od {min} do {max} €.',
    'rate': 'Ročná úroková sadzba musí byť od {min} do {max} %.',
    'years': 'Doba splácania musí byť od {min} do {max} rokov.',
}


def error_message(field: Field, code: ErrorCode) -> str:
    limits = LIMITS[field]
    return _TEMPLATES[field].format(min=format_number(limits.min, 0), max=format_number(limits.max, 0))
