from datetime import datetime
from pydantic import BaseModel, Field


class AirportOut(BaseModel):
    icao_code: str
    iata_code: str | None = None
    name: str
    country: str
    latitude: float
    longitude: float
    timezone: str

    model_config = {"from_attributes": True}


class FuelPriceOut(BaseModel):
    fuel_type: str = Field(..., examples=["JET_A1"])
    price: float = Field(..., gt=0)
    currency: str = Field(..., examples=["GBP"])
    unit: str = Field(..., examples=["LITRE"])
    tax_status: str
    source_type: str
    source_name: str
    source_url: str | None = None
    confidence_score: float = Field(..., ge=0, le=1)
    updated_at: datetime


class AirportFuelPricesOut(BaseModel):
    airport_icao: str
    airport_name: str
    fuel_prices: list[FuelPriceOut]
