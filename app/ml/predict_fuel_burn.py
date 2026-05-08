from __future__ import annotations

from fastapi import HTTPException, status

from app.ml._store import BURN_MODEL_PATH, METADATA_PATH, ensure_models, load_json
from app.ml.features import make_feature_row
from app.schemas.ml import FuelBurnPredictionRequest, FuelBurnPredictionResponse


def predict(model: dict, row: list[float]) -> float:
    """Apply the ridge model to a single feature row. Pure-Python on purpose:
    inference is one row at a time, so we avoid the numpy import on the hot path."""
    mean = model["feature_mean"]
    scale = model["feature_scale"]
    coefficients = model["coefficients"]
    z = [(value - mu) / sigma for value, mu, sigma in zip(row, mean, scale, strict=True)]
    return float(model["intercept"] + sum(coef * value for coef, value in zip(coefficients, z, strict=True)))


def predict_fuel_burn(request: FuelBurnPredictionRequest) -> FuelBurnPredictionResponse:
    try:
        ensure_models()
        model = load_json(BURN_MODEL_PATH)
        metadata = load_json(METADATA_PATH)

        row = make_feature_row(
            request.aircraft_profile,
            request.distance_nm,
            request.payload_kg,
            request.taxi_minutes,
            request.wind_component_knots,
            request.temperature_c,
        )
        predicted = max(0.0, predict(model, row))
        mape = float(metadata.get("burn_model_mape", 0.18))

        return FuelBurnPredictionResponse(
            predicted_fuel_burn_kg=round(predicted, 2),
            model=str(metadata.get("burn_model", "ridge_fuel_burn_v1")),
            model_confidence=round(max(0.5, min(0.95, 1.0 - mape)), 2),
        )
    except HTTPException:
        raise
    except Exception as exc:  # pragma: no cover
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Fuel burn model unavailable: {exc}",
        ) from exc
