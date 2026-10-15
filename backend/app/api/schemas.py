"""B10 – API kontrakt v kóde (docs/v2/api-contract.md).

Implementuje API-R1 až API-R6 pre POST /api/calculate (FR-01 až FR-05).
Mimoriadna splátka (kľúč `extra` v požiadavke, FR-06 až FR-09) pribudne s modulom B6.
"""
from typing import Literal

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

FieldKey = Literal['amount', 'rate', 'years']


class ApiModel(BaseModel):
    # camelCase v JSON (API-R2); neznámy kľúč je porušenie kontraktu → 422 (API-R6).
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, extra='forbid')


class CalculationRequest(ApiModel):
    # Surové texty z formulára (API-R3).
    amount: str  # IN-01
    rate: str    # IN-02
    years: str   # IN-03


class Results(ApiModel):
    # Hotové texty na zobrazenie (API-R4).
    monthly: str      # FR-01
    total: str        # FR-02
    interest: str     # FR-03
    extra: None = None  # FR-06 až FR-08, zatiaľ vždy null


class OkResponse(ApiModel):
    status: Literal['ok']
    results: Results


class InvalidResponse(ApiModel):
    status: Literal['invalid']
    errors: dict[FieldKey, str]  # FR-05


CalculationResponse = OkResponse | InvalidResponse
