"""B11 – endpointy.

Implementuje API-R1, API-R5 a API-R6 pre POST /api/calculate (FR-01 až FR-05), automatické uloženie
platného výpočtu (FR-10, AD-V2-14) a GET /api/health.
"""
import logging

from fastapi import APIRouter, BackgroundTasks, Depends, Request

from app.api.schemas import CalculationRequest, CalculationResponse, InvalidResponse, OkResponse, Results
from app.db.repository import CalculationRepository, StorageError
from app.input.validate import RawInput
from app.services import calculator
from app.services.calculator import SavedValues

logger = logging.getLogger(__name__)

router = APIRouter(prefix='/api')


def get_repository(request: Request) -> CalculationRepository:
    # Úložisko vytvorí B14 pri štarte. Testy ho nahradia cez app.dependency_overrides (AD-V2-09).
    return request.app.state.repository


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
    outcome = calculator.run_calculation(RawInput(amount=req.amount, rate=req.rate, years=req.years))
    if outcome.values is not None:
        background_tasks.add_task(save_calculation, repo, outcome.values)

    response = outcome.response
    if response.status == 'invalid':
        return InvalidResponse(status='invalid', errors=response.errors)
    r = response.results
    return OkResponse(status='ok', results=Results(monthly=r.monthly, total=r.total, interest=r.interest))


@router.get('/health')
def health() -> dict[str, str]:
    return {'status': 'ok'}
