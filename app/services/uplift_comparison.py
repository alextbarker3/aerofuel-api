from sqlalchemy.orm import Session

from app.schemas.fuel import (
    FuelCostEstimateRequest,
    FuelCostEstimateResponse,
    UpliftComparisonRequest,
    UpliftComparisonResponse,
)
from app.services.fuel_price_service import get_latest_price_for_product


def estimate_cost(db: Session, request: FuelCostEstimateRequest) -> FuelCostEstimateResponse:
    price = get_latest_price_for_product(db, request.airport_icao, request.fuel_type)
    return FuelCostEstimateResponse(
        airport_icao=request.airport_icao.upper(),
        fuel_type=request.fuel_type.upper(),
        uplift_litres=round(request.uplift_litres, 2),
        price_per_litre=round(price.price, 4),
        estimated_cost=round(request.uplift_litres * price.price, 2),
        currency=price.currency,
        source_name=price.source_name,
        updated_at=price.observed_at.isoformat(),
    )


def compare_uplift(db: Session, request: UpliftComparisonRequest) -> UpliftComparisonResponse:
    origin_price = get_latest_price_for_product(db, request.origin, request.fuel_type)
    destination_price = get_latest_price_for_product(db, request.destination, request.fuel_type)

    gross_saving = request.extra_uplift_litres * (destination_price.price - origin_price.price)
    net_saving = gross_saving - request.extra_burn_cost

    if net_saving > 0:
        suggested = "tanker_at_origin"
    elif net_saving < 0:
        suggested = "uplift_at_destination"
    else:
        suggested = "neutral"

    return UpliftComparisonResponse(
        origin=request.origin.upper(),
        destination=request.destination.upper(),
        fuel_type=request.fuel_type.upper(),
        origin_price_per_litre=round(origin_price.price, 4),
        destination_price_per_litre=round(destination_price.price, 4),
        gross_saving=round(gross_saving, 2),
        extra_burn_cost=round(request.extra_burn_cost, 2),
        net_saving=round(net_saving, 2),
        suggested_option=suggested,
    )
