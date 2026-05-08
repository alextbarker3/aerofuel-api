from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_db, require_api_key
from app.schemas.fuel import (
    FuelCostEstimateRequest,
    FuelCostEstimateResponse,
    FuelEstimateRequest,
    FuelEstimateResponse,
    UpliftComparisonRequest,
    UpliftComparisonResponse,
)
from app.services.fuel_estimator import estimate_fuel
from app.services.uplift_comparison import compare_uplift, estimate_cost

router = APIRouter(prefix="/fuel", tags=["fuel"], dependencies=[Depends(require_api_key)])


@router.post("/estimate", response_model=FuelEstimateResponse)
def route_fuel_estimate(request: FuelEstimateRequest, db: Session = Depends(get_db)):
    return estimate_fuel(db, request)


@router.post("/cost-estimate", response_model=FuelCostEstimateResponse)
def route_cost_estimate(request: FuelCostEstimateRequest, db: Session = Depends(get_db)):
    return estimate_cost(db, request)


@router.post("/compare-uplift", response_model=UpliftComparisonResponse)
def route_compare_uplift(request: UpliftComparisonRequest, db: Session = Depends(get_db)):
    return compare_uplift(db, request)
