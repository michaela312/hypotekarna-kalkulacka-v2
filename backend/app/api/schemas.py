"""B10 – API kontrakt v kóde (docs/v2/api-contract.md).

Implementuje API-R1 až API-R6 pre POST /api/calculate (FR-01 až FR-09),
POST /api/calculations (FR-10) a GET /api/calculations (FR-11).
Každá zmena tohto súboru musí byť aj v api-contract.md (D-V2-07).
"""
from typing import Literal

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

Mode = Literal['shorter_term', 'lower_payment']                              # IN-06
FieldKey = Literal['amount', 'rate', 'years', 'extraMonth', 'extraAmount']


class ApiModel(BaseModel):
    # camelCase v JSON (API-R2); neznámy kľúč je porušenie kontraktu → 422 (API-R6).
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, extra='forbid')


class ExtraInput(ApiModel):
    # Surové texty z formulára (API-R3). Obe prázdne = bez mimoriadnej splátky (FR-09).
    month: str    # IN-04
    amount: str   # IN-05
    mode: Mode    # IN-06, iná hodnota → 422 (API-R6)


class CalculationRequest(ApiModel):
    # Surové texty z formulára (API-R3). Všetky kľúče sú povinné, aj keď je pole prázdne.
    amount: str   # IN-01
    rate: str     # IN-02
    years: str    # IN-03
    extra: ExtraInput


class ShorterTermResult(ApiModel):                                           # FR-06, FR-08
    mode: Literal['shorter_term']
    payments: str
    last_payment: str
    total: str
    interest: str
    interest_saved: str


class LowerPaymentResult(ApiModel):                                          # FR-07, FR-08
    mode: Literal['lower_payment']
    new_monthly: str
    total: str
    interest: str
    interest_saved: str


class Results(ApiModel):
    # Hotové texty na zobrazenie (API-R4).
    monthly: str      # FR-01
    total: str        # FR-02
    interest: str     # FR-03
    extra: ShorterTermResult | LowerPaymentResult | None   # None = IN-04 aj IN-05 prázdne


class OkResponse(ApiModel):
    status: Literal['ok']
    results: Results


class InvalidResponse(ApiModel):
    status: Literal['invalid']
    errors: dict[FieldKey, str]  # FR-05, FR-09


CalculationResponse = OkResponse | InvalidResponse


class SaveResponse(ApiModel):                                                # FR-10, HTTP 201
    id: str
    created_at: str   # "15. 10. 2026 14:05" (B7a)


class SavedCalculation(ApiModel):                                            # FR-11
    id: str
    created_at: str   # "15. 10. 2026 14:05"
    amount: str       # "100 000,00 €"
    rate: str         # "4,00 %"
    years: str        # "30 rokov"
    monthly: str      # "477,42 €"
    extra: str | None # "10 000,00 € v 12. mesiaci, kratšia doba"


class CalculationList(ApiModel):                                             # FR-11, 0 až 20 položiek
    items: list[SavedCalculation]


class StorageErrorBody(ApiModel):                                            # HTTP 503
    error: Literal['storage_unavailable']
