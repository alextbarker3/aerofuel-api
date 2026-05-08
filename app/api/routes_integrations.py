from fastapi import APIRouter, Depends

from app.config import Settings, get_settings
from app.dependencies import require_api_key
from app.schemas.integrations import FuelDataStatusOut
from app.services.fuel_price_service import fuel_data_status

router = APIRouter(prefix="/integrations", tags=["integrations"], dependencies=[Depends(require_api_key)])


@router.get("/fuel-data/status", response_model=FuelDataStatusOut)
def get_fuel_data_status(settings: Settings = Depends(get_settings)):
    return fuel_data_status(settings)
