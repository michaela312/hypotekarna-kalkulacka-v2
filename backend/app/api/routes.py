"""B11 – endpointy.

Implementuje API-R1, API-R5 a API-R6 pre POST /api/calculate (FR-01 až FR-09), POST /api/calculations (FR-10,
AD-V2-12), GET /api/calculations (FR-11) a GET /api/health.
Do databázy zapisuje iba POST /api/calculations (AD-V2-15). StorageError prevedie na 503 handler v B14.
"""
from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from pydantic.alias_generators import to_camel

from app.api.schemas import (
    CalculationList, CalculationRequest, CalculationResponse, InvalidResponse, LowerPaymentResult, OkResponse,
    Results, SavedCalculation, SaveResponse, ShorterTermResult, StorageErrorBody,
)
from app.db.repository import CalculationRepository, SavedRecord
from app.format.datetime import format_datetime
from app.format.money import format_money, format_rate
from app.input.validate import RawInput
from app.services import calculator
from app.text.messages import extra_text, years_text

router = APIRouter(prefix='/api')


def get_repository(request: Request) -> CalculationRepository:
    # Úložisko vytvorí B14 pri štarte. Testy ho nahradia cez app.dependency_overrides (AD-V2-09).
    return request.app.state.repository


def to_raw_input(req: CalculationRequest) -> RawInput:
    return RawInput(amount=req.amount, rate=req.rate, years=req.years,
                    extra_month=req.extra.month, extra_amount=req.extra.amount, mode=req.extra.mode)


def to_api_response(response: calculator.CalculationResponse) -> CalculationResponse:
    if response.status == 'invalid':
        # Kľúče chýb v JSON sú camelCase (API-R2): extra_month → extraMonth.
        return InvalidResponse(status='invalid', errors={to_camel(k): v for k, v in response.errors.items()})
    r = response.results
    extra = None
    if r.extra is not None and r.extra.mode == 'shorter_term':
        extra = ShorterTermResult(mode='shorter_term', payments=r.extra.payments, last_payment=r.extra.last_payment,
                                  total=r.extra.total, interest=r.extra.interest, interest_saved=r.extra.interest_saved)
    elif r.extra is not None:
        extra = LowerPaymentResult(mode='lower_payment', new_monthly=r.extra.new_monthly, total=r.extra.total,
                                   interest=r.extra.interest, interest_saved=r.extra.interest_saved)
    return OkResponse(status='ok', results=Results(monthly=r.monthly, total=r.total, interest=r.interest, extra=extra))


def to_saved_calculation(record: SavedRecord) -> SavedCalculation:
    # FR-11: hotové texty cez B7, B7a a B8 (API-R4).
    values = record.values
    extra = values.extra
    return SavedCalculation(
        id=record.id,
        created_at=format_datetime(record.created_at),
        amount=format_money(values.amount),
        rate=format_rate(values.rate),
        years=years_text(values.years),
        monthly=format_money(values.monthly_payment),
        extra=None if extra is None else extra_text(extra.amount, extra.month, extra.mode),
    )


@router.post('/calculate', response_model=CalculationResponse)
def calculate(req: CalculationRequest) -> CalculationResponse:
    # Neplatný vstup používateľa je HTTP 200 so status 'invalid' (API-R5, AD-V2-03). Nič neukladá (AD-V2-15).
    return to_api_response(calculator.run_calculation(to_raw_input(req)).response)


@router.post('/calculations', status_code=201, response_model=SaveResponse,
             responses={422: {'model': InvalidResponse}, 503: {'model': StorageErrorBody}})
def save(req: CalculationRequest, repo: CalculationRepository = Depends(get_repository)):
    # AD-V2-12: výpočet sa urobí znova, výsledkom z frontendu sa neverí (požiadavka ich ani nemôže obsahovať).
    outcome = calculator.run_calculation(to_raw_input(req))
    if outcome.values is None:
        return JSONResponse(to_api_response(outcome.response).model_dump(by_alias=True), status_code=422)
    record = repo.save(outcome.values)
    return SaveResponse(id=record.id, created_at=format_datetime(record.created_at))


@router.get('/calculations', response_model=CalculationList, responses={503: {'model': StorageErrorBody}})
def list_calculations(repo: CalculationRepository = Depends(get_repository)) -> CalculationList:
    return CalculationList(items=[to_saved_calculation(r) for r in repo.list_latest()])


@router.get('/health')
def health() -> dict[str, str]:
    return {'status': 'ok'}
