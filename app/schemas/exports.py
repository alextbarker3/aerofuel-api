from pydantic import BaseModel


class EstimateLogRow(BaseModel):
    created_at: str
    origin: str
    destination: str
    aircraft_profile: str
    estimated_total_fuel_kg: float
    estimated_cost: float | None = None
    predicted_burn_kg: float | None = None
    anomaly_flag: str
    note: str | None = None
