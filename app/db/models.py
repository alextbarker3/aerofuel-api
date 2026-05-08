from datetime import UTC, date, datetime

from sqlalchemy import Date, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class Airport(Base):
    __tablename__ = "airports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    icao_code: Mapped[str] = mapped_column(String(4), unique=True, index=True, nullable=False)
    iata_code: Mapped[str | None] = mapped_column(String(3))
    name: Mapped[str] = mapped_column(Text, nullable=False)
    country: Mapped[str] = mapped_column(Text, nullable=False)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    timezone: Mapped[str] = mapped_column(Text, default="UTC")

    prices: Mapped[list["FuelPriceObservation"]] = relationship(back_populates="airport")


class FuelProduct(Base):
    __tablename__ = "fuel_products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String(32), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    density_kg_per_litre: Mapped[float] = mapped_column(Float, nullable=False)
    emissions_factor_kg_co2_per_kg: Mapped[float] = mapped_column(Float, default=3.16)

    prices: Mapped[list["FuelPriceObservation"]] = relationship(back_populates="fuel_product")


class FuelPriceObservation(Base):
    __tablename__ = "fuel_price_observations"
    __table_args__ = (
        UniqueConstraint("airport_id", "fuel_product_id", "observed_at", name="uq_fuel_price_observation"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    airport_id: Mapped[int] = mapped_column(ForeignKey("airports.id"), nullable=False)
    fuel_product_id: Mapped[int] = mapped_column(ForeignKey("fuel_products.id"), nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    unit: Mapped[str] = mapped_column(String(16), nullable=False)
    tax_status: Mapped[str] = mapped_column(String(32), default="UNKNOWN")
    source_type: Mapped[str] = mapped_column(String(64), default="synthetic")
    source_name: Mapped[str] = mapped_column(Text, default="synthetic_provider")
    source_url: Mapped[str | None] = mapped_column(Text)
    confidence_score: Mapped[float] = mapped_column(Float, default=0.75)
    observed_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    airport: Mapped[Airport] = relationship(back_populates="prices")
    fuel_product: Mapped[FuelProduct] = relationship(back_populates="prices")


class AircraftProfile(Base):
    __tablename__ = "aircraft_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    profile_name: Mapped[str] = mapped_column(String(128), unique=True, index=True, nullable=False)
    category: Mapped[str] = mapped_column(String(64), nullable=False)
    base_burn_kg_per_nm: Mapped[float] = mapped_column(Float, nullable=False)
    taxi_burn_kg_per_min: Mapped[float] = mapped_column(Float, nullable=False)
    reserve_burn_kg_per_min: Mapped[float] = mapped_column(Float, nullable=False)
    payload_penalty_kg_per_1000kg_per_nm: Mapped[float] = mapped_column(Float, default=0.015)
    headwind_penalty_kg_per_knot_nm: Mapped[float] = mapped_column(Float, default=0.005)


class SyntheticFlight(Base):
    __tablename__ = "synthetic_flights"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    aircraft_profile_id: Mapped[int] = mapped_column(ForeignKey("aircraft_profiles.id"), nullable=False)
    origin_airport_id: Mapped[int] = mapped_column(ForeignKey("airports.id"), nullable=False)
    destination_airport_id: Mapped[int] = mapped_column(ForeignKey("airports.id"), nullable=False)
    distance_nm: Mapped[float] = mapped_column(Float, nullable=False)
    payload_kg: Mapped[float] = mapped_column(Float, nullable=False)
    taxi_minutes: Mapped[float] = mapped_column(Float, nullable=False)
    wind_component_knots: Mapped[float] = mapped_column(Float, nullable=False)
    temperature_c: Mapped[float] = mapped_column(Float, nullable=False)
    planned_burn_kg: Mapped[float] = mapped_column(Float, nullable=False)
    actual_burn_kg: Mapped[float] = mapped_column(Float, nullable=False)
    flight_date: Mapped[date] = mapped_column(Date, nullable=False)

    aircraft_profile: Mapped[AircraftProfile] = relationship()
    origin_airport: Mapped[Airport] = relationship(foreign_keys=[origin_airport_id])
    destination_airport: Mapped[Airport] = relationship(foreign_keys=[destination_airport_id])


class FuelEstimateLog(Base):
    __tablename__ = "fuel_estimate_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))
    origin_icao: Mapped[str] = mapped_column(String(4), nullable=False)
    destination_icao: Mapped[str] = mapped_column(String(4), nullable=False)
    aircraft_profile: Mapped[str] = mapped_column(String(128), nullable=False)
    estimated_total_fuel_kg: Mapped[float] = mapped_column(Float, nullable=False)
    estimated_cost: Mapped[float | None] = mapped_column(Float)
    predicted_burn_kg: Mapped[float | None] = mapped_column(Float)
    anomaly_flag: Mapped[str] = mapped_column(String(8), default="false")
    note: Mapped[str | None] = mapped_column(Text)
