from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.database import Base, engine
from app.db.models import Airport, AircraftProfile, FuelPriceObservation, FuelProduct, SyntheticFlight

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"


def create_tables() -> None:
    Base.metadata.create_all(bind=engine)


def _get_or_create_airport(db: Session, row: dict) -> Airport:
    existing = db.scalar(select(Airport).where(Airport.icao_code == row["icao_code"]))
    if existing:
        return existing
    airport = Airport(
        icao_code=row["icao_code"],
        iata_code=row.get("iata_code") or None,
        name=row["name"],
        country=row["country"],
        latitude=float(row["latitude"]),
        longitude=float(row["longitude"]),
        timezone=row.get("timezone") or "UTC",
    )
    db.add(airport)
    db.flush()
    return airport


def _get_or_create_fuel_product(db: Session, row: dict) -> FuelProduct:
    existing = db.scalar(select(FuelProduct).where(FuelProduct.code == row["code"]))
    if existing:
        return existing
    product = FuelProduct(
        code=row["code"],
        name=row["name"],
        density_kg_per_litre=float(row["density_kg_per_litre"]),
        emissions_factor_kg_co2_per_kg=float(row["emissions_factor_kg_co2_per_kg"]),
    )
    db.add(product)
    db.flush()
    return product


def seed_database(db: Session) -> None:
    create_tables()

    with open(DATA_DIR / "synthetic_airports.csv", newline="", encoding="utf-8") as f:
        airports = {row["icao_code"]: _get_or_create_airport(db, row) for row in csv.DictReader(f)}

    with open(DATA_DIR / "fuel_products.csv", newline="", encoding="utf-8") as f:
        products = {row["code"]: _get_or_create_fuel_product(db, row) for row in csv.DictReader(f)}

    if not db.scalar(select(AircraftProfile).limit(1)):
        with open(DATA_DIR / "synthetic_aircraft_profiles.csv", newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                db.add(
                    AircraftProfile(
                        profile_name=row["profile_name"],
                        category=row["category"],
                        base_burn_kg_per_nm=float(row["base_burn_kg_per_nm"]),
                        taxi_burn_kg_per_min=float(row["taxi_burn_kg_per_min"]),
                        reserve_burn_kg_per_min=float(row["reserve_burn_kg_per_min"]),
                        payload_penalty_kg_per_1000kg_per_nm=float(row["payload_penalty_kg_per_1000kg_per_nm"]),
                        headwind_penalty_kg_per_knot_nm=float(row["headwind_penalty_kg_per_knot_nm"]),
                    )
                )
        db.flush()

    if not db.scalar(select(FuelPriceObservation).limit(1)):
        with open(DATA_DIR / "synthetic_fuel_prices.csv", newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                db.add(
                    FuelPriceObservation(
                        airport_id=airports[row["airport_icao"]].id,
                        fuel_product_id=products[row["fuel_type"]].id,
                        price=float(row["price"]),
                        currency=row["currency"],
                        unit=row["unit"],
                        tax_status=row["tax_status"],
                        source_type=row["source_type"],
                        source_name=row["source_name"],
                        source_url=row.get("source_url") or None,
                        confidence_score=float(row["confidence_score"]),
                        observed_at=datetime.fromisoformat(row["observed_at"]),
                    )
                )

    if not db.scalar(select(SyntheticFlight).limit(1)):
        aircraft_by_name = {a.profile_name: a for a in db.scalars(select(AircraftProfile)).all()}
        with open(DATA_DIR / "synthetic_flights.csv", newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                db.add(
                    SyntheticFlight(
                        aircraft_profile_id=aircraft_by_name[row["aircraft_profile"]].id,
                        origin_airport_id=airports[row["origin"]].id,
                        destination_airport_id=airports[row["destination"]].id,
                        distance_nm=float(row["distance_nm"]),
                        payload_kg=float(row["payload_kg"]),
                        taxi_minutes=float(row["taxi_minutes"]),
                        wind_component_knots=float(row["wind_component_knots"]),
                        temperature_c=float(row["temperature_c"]),
                        planned_burn_kg=float(row["planned_burn_kg"]),
                        actual_burn_kg=float(row["actual_burn_kg"]),
                        flight_date=datetime.strptime(row["flight_date"], "%Y-%m-%d").date(),
                    )
                )

    db.commit()
