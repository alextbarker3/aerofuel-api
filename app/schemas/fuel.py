from pydantic import BaseModel, Field, field_validator


class FuelEstimateRequest(BaseModel):
    aircraft_profile: str = Field(..., examples=["generic_transport_aircraft"])
    origin: str = Field(..., min_length=4, max_length=4, examples=["EGTK"])
    destination: str = Field(..., min_length=4, max_length=4, examples=["EGSS"])
    distance_nm: float = Field(..., gt=0, le=10000)
    payload_kg: float = Field(..., ge=0, le=200000)
    taxi_minutes: float = Field(..., ge=0, le=180)
    wind_component_knots: float = Field(0, ge=-200, le=200, description="Positive = tailwind, negative = headwind")
    temperature_c: float = Field(15, ge=-80, le=60)
    contingency_percent: float = Field(5.0, ge=0, le=30)
    final_reserve_minutes: float = Field(45, ge=0, le=180)

    @field_validator("origin", "destination")
    @classmethod
    def uppercase_icao(cls, value: str) -> str:
        return value.upper()


class FuelBreakdown(BaseModel):
    taxi: float
    trip: float
    contingency: float
    final_reserve: float
    total: float


class FuelEstimateResponse(BaseModel):
    aircraft_profile: str
    origin: str
    destination: str
    fuel_required_kg: FuelBreakdown
    estimated_co2_kg: float


class FuelCostEstimateRequest(BaseModel):
    airport_icao: str = Field(..., min_length=4, max_length=4, examples=["EGTK"])
    fuel_type: str = Field("JET_A1")
    uplift_litres: float = Field(..., gt=0, le=500000)

    @field_validator("airport_icao", "fuel_type")
    @classmethod
    def uppercase_fields(cls, value: str) -> str:
        return value.upper()


class FuelCostEstimateResponse(BaseModel):
    airport_icao: str
    fuel_type: str
    uplift_litres: float
    price_per_litre: float
    estimated_cost: float
    currency: str
    source_name: str
    updated_at: str


class UpliftComparisonRequest(BaseModel):
    origin: str = Field(..., min_length=4, max_length=4)
    destination: str = Field(..., min_length=4, max_length=4)
    fuel_type: str = Field("JET_A1")
    extra_uplift_litres: float = Field(0, ge=0, le=100000)
    extra_burn_cost: float = Field(0, ge=0)

    @field_validator("origin", "destination", "fuel_type")
    @classmethod
    def uppercase_fields(cls, value: str) -> str:
        return value.upper()


class UpliftComparisonResponse(BaseModel):
    origin: str
    destination: str
    fuel_type: str
    origin_price_per_litre: float
    destination_price_per_litre: float
    gross_saving: float
    extra_burn_cost: float
    net_saving: float
    suggested_option: str
