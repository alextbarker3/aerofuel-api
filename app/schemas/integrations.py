from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.airports import FuelPriceOut


class FuelDataStatusOut(BaseModel):
    mode: str
    live_fuel_enabled: bool
    provider_name: str | None
    provider_configured: bool
    allowed_hosts: list[str]
    transport: str
    note: str


class FuelPriceRefreshOut(BaseModel):
    airport_icao: str = Field(..., examples=["EGTK"])
    refreshed_at: datetime
    rows_cached: int
    fuel_prices: list[FuelPriceOut]
