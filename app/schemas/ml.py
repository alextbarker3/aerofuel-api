from pydantic import BaseModel, Field


class FuelBurnPredictionRequest(BaseModel):
    aircraft_profile: str = Field("generic_transport_aircraft", examples=["generic_transport_aircraft"])
    distance_nm: float = Field(..., gt=0, le=10_000)
    payload_kg: float = Field(..., ge=0, le=200_000)
    taxi_minutes: float = Field(..., ge=0, le=180)
    wind_component_knots: float = Field(0, ge=-200, le=200)
    temperature_c: float = Field(15, ge=-80, le=60)


class FuelBurnPredictionResponse(BaseModel):
    predicted_fuel_burn_kg: float
    model: str
    model_confidence: float = Field(..., ge=0, le=1)


class FuelAnomalyRequest(BaseModel):
    actual_burn_kg: float = Field(..., gt=0)
    distance_nm: float = Field(..., gt=0, le=10_000)
    payload_kg: float = Field(..., ge=0, le=200_000)
    taxi_minutes: float = Field(..., ge=0, le=180)
    aircraft_profile: str = "generic_transport_aircraft"
    wind_component_knots: float = Field(0, ge=-200, le=200)
    temperature_c: float = Field(15, ge=-80, le=60)


class FuelAnomalyResponse(BaseModel):
    anomaly_flag: bool
    expected_burn_kg: float
    variance_percent: float
    severity: str
    possible_factors: list[str]
