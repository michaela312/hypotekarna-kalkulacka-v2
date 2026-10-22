"""B11 – endpointy.

Implementuje API-R1, API-R5 a API-R6 pre POST /api/calculate (FR-01 až FR-09), automatické uloženie
platného výpočtu (FR-10, AD-V2-14) a GET /api/health.
"""
import logging

from fastapi import APIRouter, BackgroundTasks, Depends, Request
from pydantic.alias_generators import to_camel

from app.api.schemas import (
    CalculationRequest, CalculationResponse, InvalidResponse, LowerPaymentResult, OkResponse, Results,
    ShorterTermResult,
)
from app.db.repository import CalculationRepository, StorageError
from app.input.validate import RawInput
from app.services import calculator
from app.services.calculator import SavedValues

logger = logging.getLogger(__name__)

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


def save_calculation(repo: CalculationRepository, values: SavedValues) -> None:
    # Beží až po odoslaní odpovede. Chyba databázy nesmie pokaziť výpočet, iba sa zapíše do logu.
    try:
        repo.save(values)
    except StorageError as err:
        logger.warning('%s', err)


@router.post('/calculate', response_model=CalculationResponse)
def calculate(
    req: CalculationRequest,
    background_tasks: BackgroundTasks,
    repo: CalculationRepository = Depends(get_repository),
) -> CalculationResponse:
    # Neplatný vstup používateľa je HTTP 200 so status 'invalid' (API-R5, AD-V2-03) a neukladá sa.
    outcome = calculator.run_calculation(to_raw_input(req))
    if outcome.values is not None:
        background_tasks.add_task(save_calculation, repo, outcome.values)
    return to_api_response(outcome.response)


@router.get('/health')
def health() -> dict[str, str]:
    return {'status': 'ok'}
