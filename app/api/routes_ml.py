from fastapi import APIRouter, Depends

from app.dependencies import require_api_key
from app.ml.check_anomaly import check_fuel_anomaly
from app.ml.predict_fuel_burn import predict_fuel_burn
from app.schemas.ml import (
    FuelAnomalyRequest,
    FuelAnomalyResponse,
    FuelBurnPredictionRequest,
    FuelBurnPredictionResponse,
)

router = APIRouter(prefix="/ml", tags=["machine-learning"], dependencies=[Depends(require_api_key)])


@router.post("/predict-fuel-burn", response_model=FuelBurnPredictionResponse)
def route_predict_fuel_burn(request: FuelBurnPredictionRequest):
    return predict_fuel_burn(request)


@router.post("/check-fuel-anomaly", response_model=FuelAnomalyResponse)
def route_check_fuel_anomaly(request: FuelAnomalyRequest):
    return check_fuel_anomaly(request)
