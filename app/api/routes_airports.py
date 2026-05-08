from datetime import UTC, datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.config import Settings, get_settings
from app.dependencies import get_db, require_api_key
from app.db.models import Airport
from app.schemas.airports import AirportFuelPricesOut, AirportOut, FuelPriceOut
from app.schemas.integrations import FuelPriceRefreshOut
from app.services.fuel_price_service import (
    get_airport_by_icao,
    get_latest_fuel_prices,
    refresh_external_fuel_prices,
)

router = APIRouter(prefix="/airports", tags=["airports"], dependencies=[Depends(require_api_key)])


@router.get("", response_model=list[AirportOut])
def list_airports(
    country: str | None = Query(default=None),
    q: str | None = Query(default=None, description="Search ICAO, IATA, name or country"),
    limit: int = Query(default=50, ge=1, le=500),
    db: Session = Depends(get_db),
):
    statement = select(Airport)

    if country:
        statement = statement.where(Airport.country.ilike(country))

    if q:
        term = f"%{q}%"
        statement = statement.where(
            or_(
                Airport.icao_code.ilike(term),
                Airport.iata_code.ilike(term),
                Airport.name.ilike(term),
                Airport.country.ilike(term),
            )
        )

    return db.scalars(statement.order_by(Airport.icao_code).limit(limit)).all()


@router.get("/{icao}", response_model=AirportOut)
def get_airport(icao: str, db: Session = Depends(get_db)):
    return get_airport_by_icao(db, icao)


@router.get("/{icao}/fuel-prices", response_model=AirportFuelPricesOut)
async def get_fuel_prices(
    icao: str,
    refresh: bool = Query(default=False, description="Fetch from the configured live provider before returning cached prices"),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
):
    airport = get_airport_by_icao(db, icao)
    prices = await refresh_external_fuel_prices(db, icao, settings) if refresh else get_latest_fuel_prices(db, icao)

    return AirportFuelPricesOut(
        airport_icao=airport.icao_code,
        airport_name=airport.name,
        fuel_prices=_price_outputs(prices),
    )


@router.post("/{icao}/fuel-prices/refresh", response_model=FuelPriceRefreshOut)
async def refresh_fuel_prices(
    icao: str,
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
):
    airport = get_airport_by_icao(db, icao)
    prices = await refresh_external_fuel_prices(db, icao, settings)
    return FuelPriceRefreshOut(
        airport_icao=airport.icao_code,
        refreshed_at=datetime.now(UTC),
        rows_cached=len(prices),
        fuel_prices=_price_outputs(prices),
    )


def _price_outputs(prices):
    return [
        FuelPriceOut(
            fuel_type=price.fuel_product.code,
            price=round(price.price, 4),
            currency=price.currency,
            unit=price.unit,
            tax_status=price.tax_status,
            source_type=price.source_type,
            source_name=price.source_name,
            source_url=price.source_url,
            confidence_score=round(price.confidence_score, 2),
            updated_at=price.observed_at,
        )
        for price in prices
    ]
