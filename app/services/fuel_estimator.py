from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import AircraftProfile, FuelEstimateLog, FuelProduct
from app.schemas.fuel import FuelBreakdown, FuelEstimateRequest, FuelEstimateResponse

DEFAULT_CO2_FACTOR_KG_PER_KG = 3.16
STANDARD_DAY_C = 15.0
HOT_DAY_BURN_PENALTY_KG_PER_C = 0.8


def _aircraft_profile(db: Session, name: str) -> AircraftProfile:
    profile = db.scalar(select(AircraftProfile).where(AircraftProfile.profile_name == name))
    if profile is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Aircraft profile not found: {name}")
    return profile


def _jet_a1_emissions_factor(db: Session) -> float:
    product = db.scalar(select(FuelProduct).where(FuelProduct.code == "JET_A1"))
    return product.emissions_factor_kg_co2_per_kg if product else DEFAULT_CO2_FACTOR_KG_PER_KG


def estimate_fuel(db: Session, request: FuelEstimateRequest, *, log_result: bool = True) -> FuelEstimateResponse:
    profile = _aircraft_profile(db, request.aircraft_profile)

    distance_burn = request.distance_nm * profile.base_burn_kg_per_nm
    payload_burn = (request.payload_kg / 1_000) * profile.payload_penalty_kg_per_1000kg_per_nm * request.distance_nm
    wind_burn = -request.wind_component_knots * profile.headwind_penalty_kg_per_knot_nm * request.distance_nm
    temperature_burn = max(0.0, request.temperature_c - STANDARD_DAY_C) * HOT_DAY_BURN_PENALTY_KG_PER_C

    trip = max(0.0, distance_burn + payload_burn + wind_burn + temperature_burn)
    taxi = request.taxi_minutes * profile.taxi_burn_kg_per_min
    contingency = trip * request.contingency_percent / 100
    final_reserve = request.final_reserve_minutes * profile.reserve_burn_kg_per_min
    total = taxi + trip + contingency + final_reserve

    response = FuelEstimateResponse(
        aircraft_profile=request.aircraft_profile,
        origin=request.origin,
        destination=request.destination,
        fuel_required_kg=FuelBreakdown(
            taxi=round(taxi, 2),
            trip=round(trip, 2),
            contingency=round(contingency, 2),
            final_reserve=round(final_reserve, 2),
            total=round(total, 2),
        ),
        estimated_co2_kg=round(total * _jet_a1_emissions_factor(db), 2),
    )

    if log_result:
        db.add(
            FuelEstimateLog(
                origin_icao=response.origin,
                destination_icao=response.destination,
                aircraft_profile=response.aircraft_profile,
                estimated_total_fuel_kg=response.fuel_required_kg.total,
                note="fuel_estimate",
            )
        )
        db.commit()

    return response
