from __future__ import annotations

import logging

from fastapi import HTTPException, status
from sqlalchemy import desc, select
from sqlalchemy.orm import Session, selectinload

from app.config import Settings
from app.db.models import Airport, FuelPriceObservation, FuelProduct
from app.integrations.fuel_price_provider import ExternalFuelPriceProvider, NormalizedFuelPrice


logger = logging.getLogger(__name__)


DEFAULT_PRODUCTS = {
    "JET_A1": {"name": "Jet A-1", "density": 0.80, "co2": 3.16},
    "JET_A": {"name": "Jet A", "density": 0.80, "co2": 3.16},
    "AVGAS_100LL": {"name": "Avgas 100LL", "density": 0.72, "co2": 3.10},
    "SAF_BLEND": {"name": "Sustainable Aviation Fuel Blend", "density": 0.79, "co2": 2.20},
}


def get_airport_by_icao(db: Session, icao: str) -> Airport:
    airport = db.scalar(select(Airport).where(Airport.icao_code == icao.upper()))
    if airport is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Airport not found: {icao.upper()}")
    return airport


def get_latest_fuel_prices(db: Session, icao: str) -> list[FuelPriceObservation]:
    airport = get_airport_by_icao(db, icao)
    product_ids = db.scalars(select(FuelProduct.id)).all()
    rows: list[FuelPriceObservation] = []

    for product_id in product_ids:
        price = db.scalar(
            select(FuelPriceObservation)
            .options(selectinload(FuelPriceObservation.fuel_product))
            .where(
                FuelPriceObservation.airport_id == airport.id,
                FuelPriceObservation.fuel_product_id == product_id,
            )
            .order_by(desc(FuelPriceObservation.observed_at))
            .limit(1)
        )
        if price is not None:
            rows.append(price)

    return rows


def get_latest_price_for_product(db: Session, airport_icao: str, fuel_type: str) -> FuelPriceObservation:
    airport = get_airport_by_icao(db, airport_icao)
    product = db.scalar(select(FuelProduct).where(FuelProduct.code == fuel_type.upper()))
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Fuel product not found: {fuel_type.upper()}")

    price = db.scalar(
        select(FuelPriceObservation)
        .where(FuelPriceObservation.airport_id == airport.id, FuelPriceObservation.fuel_product_id == product.id)
        .order_by(desc(FuelPriceObservation.observed_at))
        .limit(1)
    )
    if price is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No {fuel_type.upper()} price found for {airport_icao.upper()}",
        )
    return price


async def refresh_external_fuel_prices(db: Session, icao: str, settings: Settings) -> list[FuelPriceObservation]:
    """Pull live fuel prices from the configured provider and cache them locally."""
    airport = get_airport_by_icao(db, icao)
    provider = ExternalFuelPriceProvider(settings)
    provider_rows = await provider.fetch_airport_prices(icao)

    observations = [_upsert_price_observation(db, airport, row) for row in provider_rows]
    db.commit()

    for observation in observations:
        db.refresh(observation)

    logger.info("refreshed %d fuel price rows for %s from %s", len(observations), airport.icao_code, settings.external_fuel_provider_name)
    return observations


def fuel_data_status(settings: Settings) -> dict[str, object]:
    parsed_base_url = settings.external_fuel_api_base_url or None
    return {
        "mode": settings.fuel_data_mode,
        "live_fuel_enabled": settings.live_fuel_enabled,
        "provider_name": settings.external_fuel_provider_name if parsed_base_url else None,
        "provider_configured": bool(parsed_base_url),
        "allowed_hosts": settings.parsed_external_fuel_allowed_hosts,
        "transport": "outbound_https_only",
        "note": "Live provider calls are disabled until EXTERNAL_FUEL_API_BASE_URL is configured.",
    }


def _upsert_price_observation(
    db: Session,
    airport: Airport,
    row: NormalizedFuelPrice,
) -> FuelPriceObservation:
    product = _get_or_create_product(db, row.fuel_type)
    observed_at = row.observed_at.replace(tzinfo=None)

    existing = db.scalar(
        select(FuelPriceObservation).where(
            FuelPriceObservation.airport_id == airport.id,
            FuelPriceObservation.fuel_product_id == product.id,
            FuelPriceObservation.observed_at == observed_at,
        )
    )
    if existing:
        existing.price = row.price
        existing.currency = row.currency
        existing.unit = row.unit
        existing.tax_status = row.tax_status
        existing.source_type = row.source_type
        existing.source_name = row.source_name
        existing.source_url = row.source_url
        existing.confidence_score = row.confidence_score
        return existing

    observation = FuelPriceObservation(
        airport_id=airport.id,
        fuel_product_id=product.id,
        price=row.price,
        currency=row.currency,
        unit=row.unit,
        tax_status=row.tax_status,
        source_type=row.source_type,
        source_name=row.source_name,
        source_url=row.source_url,
        confidence_score=row.confidence_score,
        observed_at=observed_at,
    )
    db.add(observation)
    db.flush()
    return observation


def _get_or_create_product(db: Session, code: str) -> FuelProduct:
    code = code.upper()
    existing = db.scalar(select(FuelProduct).where(FuelProduct.code == code))
    if existing:
        return existing

    defaults = DEFAULT_PRODUCTS.get(code, {"name": code.replace("_", " ").title(), "density": 0.80, "co2": 3.16})
    product = FuelProduct(
        code=code,
        name=defaults["name"],
        density_kg_per_litre=defaults["density"],
        emissions_factor_kg_co2_per_kg=defaults["co2"],
    )
    db.add(product)
    db.flush()
    return product
