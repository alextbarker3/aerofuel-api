from __future__ import annotations

from fastapi import HTTPException, status

from app.ml._store import ANOMALY_MODEL_PATH, BURN_MODEL_PATH, ensure_models, load_json
from app.ml.features import make_feature_row
from app.ml.predict_fuel_burn import predict
from app.schemas.ml import FuelAnomalyRequest, FuelAnomalyResponse


def _severity(score: float, model: dict) -> str:
    if score >= model["high_threshold_sigma"]:
        return "high"
    if score >= model["medium_threshold_sigma"]:
        return "medium"
    if score >= model["low_threshold_sigma"]:
        return "low"
    return "normal"


def _possible_factors(request: FuelAnomalyRequest, expected_burn_kg: float) -> list[str]:
    factors = [
        "actual burn exceeded model estimate"
        if request.actual_burn_kg > expected_burn_kg
        else "actual burn was below model estimate"
    ]
    if request.taxi_minutes > 15:
        factors.append("extended taxi time")
    if request.wind_component_knots < -5:
        factors.append("headwind component")
    if request.payload_kg > 5_000:
        factors.append("higher payload")
    return factors


def check_fuel_anomaly(request: FuelAnomalyRequest) -> FuelAnomalyResponse:
    try:
        ensure_models()
        burn_model = load_json(BURN_MODEL_PATH)
        anomaly_model = load_json(ANOMALY_MODEL_PATH)

        row = make_feature_row(
            request.aircraft_profile,
            request.distance_nm,
            request.payload_kg,
            request.taxi_minutes,
            request.wind_component_knots,
            request.temperature_c,
        )
        expected = max(1.0, predict(burn_model, row))
        variance_percent = 100.0 * (request.actual_burn_kg - expected) / expected
        score = abs(variance_percent - anomaly_model["residual_centre_pct"]) / anomaly_model["residual_sigma_pct"]
        severity = _severity(score, anomaly_model)

        return FuelAnomalyResponse(
            anomaly_flag=severity in {"medium", "high"},
            expected_burn_kg=round(expected, 2),
            variance_percent=round(variance_percent, 2),
            severity=severity,
            possible_factors=_possible_factors(request, expected),
        )
    except HTTPException:
        raise
    except Exception as exc:  # pragma: no cover
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Fuel anomaly model unavailable: {exc}",
        ) from exc
