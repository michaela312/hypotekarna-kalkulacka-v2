"""B11 – endpointy.

Implementuje API-R1, API-R5 a API-R6 pre POST /api/calculate (FR-01 až FR-05) a GET /api/health.
"""
from fastapi import APIRouter

from app.api.schemas import CalculationRequest, CalculationResponse, InvalidResponse, OkResponse, Results
from app.input.validate import RawInput
from app.services import calculator

router = APIRouter(prefix='/api')


@router.post('/calculate', response_model=CalculationResponse)
def calculate(req: CalculationRequest) -> CalculationResponse:
    # Neplatný vstup používateľa je HTTP 200 so status 'invalid' (API-R5, AD-V2-03).
    outcome = calculator.run_calculation(RawInput(amount=req.amount, rate=req.rate, years=req.years))
    if outcome.status == 'invalid':
        return InvalidResponse(status='invalid', errors=outcome.errors)
    r = outcome.results
    return OkResponse(status='ok', results=Results(monthly=r.monthly, total=r.total, interest=r.interest))


@router.get('/health')
def health() -> dict[str, str]:
    return {'status': 'ok'}
