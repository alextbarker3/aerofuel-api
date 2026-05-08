from __future__ import annotations

import csv
import json
import logging
from pathlib import Path
from typing import Any

import numpy as np

from app.ml._store import ANOMALY_MODEL_PATH, BURN_MODEL_PATH, METADATA_PATH, MODEL_DIR
from app.ml.features import FEATURE_NAMES, make_feature_row

DATA_PATH = Path(__file__).resolve().parents[2] / "data" / "synthetic_flights.csv"
RIDGE_LAMBDA = 1e-3
MAD_TO_SIGMA = 1.4826  # MAD-to-sigma scaling for residuals assumed approximately Gaussian

logger = logging.getLogger(__name__)


def _rows(path: Path = DATA_PATH) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _matrix(rows: list[dict[str, str]]) -> tuple[np.ndarray, np.ndarray]:
    features = [
        make_feature_row(
            aircraft_profile=row["aircraft_profile"],
            distance_nm=float(row["distance_nm"]),
            payload_kg=float(row["payload_kg"]),
            taxi_minutes=float(row["taxi_minutes"]),
            wind_component_knots=float(row["wind_component_knots"]),
            temperature_c=float(row["temperature_c"]),
        )
        for row in rows
    ]
    target = [float(row["actual_burn_kg"]) for row in rows]
    return np.asarray(features, dtype=float), np.asarray(target, dtype=float)


def _fit_ridge(X: np.ndarray, y: np.ndarray) -> dict[str, Any]:
    mean = X.mean(axis=0)
    scale = X.std(axis=0)
    scale[scale == 0] = 1.0

    Xz = (X - mean) / scale
    design = np.column_stack([np.ones(len(Xz)), Xz])

    penalty = RIDGE_LAMBDA * np.eye(design.shape[1])
    penalty[0, 0] = 0.0  # do not regularise the intercept

    beta = np.linalg.solve(design.T @ design + penalty, design.T @ y)
    fitted = design @ beta
    mape = _safe_mape(y, fitted)

    return {
        "model": "ridge_fuel_burn_v1",
        "feature_names": FEATURE_NAMES,
        "intercept": float(beta[0]),
        "coefficients": [float(value) for value in beta[1:]],
        "feature_mean": [float(value) for value in mean],
        "feature_scale": [float(value) for value in scale],
        "training_rows": int(len(y)),
        "mape": mape,
    }


def _safe_mape(y: np.ndarray, fitted: np.ndarray, eps: float = 1.0) -> float:
    """MAPE with a denominator floor to avoid blow-up on near-zero targets."""
    denom = np.maximum(np.abs(y), eps)
    return float(np.mean(np.abs((y - fitted) / denom)))


def _predict_in_sample(model: dict[str, Any], X: np.ndarray) -> np.ndarray:
    """Vectorised in-sample prediction used during training only."""
    mean = np.asarray(model["feature_mean"], dtype=float)
    scale = np.asarray(model["feature_scale"], dtype=float)
    beta = np.asarray(model["coefficients"], dtype=float)
    return float(model["intercept"]) + ((X - mean) / scale) @ beta


def _fit_residual_model(y: np.ndarray, fitted: np.ndarray) -> dict[str, Any]:
    safe_fitted = np.where(np.abs(fitted) > 1e-6, fitted, 1e-6)
    residual_pct = 100.0 * (y - fitted) / safe_fitted
    centre = float(np.median(residual_pct))
    mad = float(np.median(np.abs(residual_pct - centre)))
    sigma = max(MAD_TO_SIGMA * mad, 1e-6)

    return {
        "model": "robust_residual_v1",
        "residual_centre_pct": centre,
        "residual_sigma_pct": sigma,
        "low_threshold_sigma": 2.0,
        "medium_threshold_sigma": 3.0,
        "high_threshold_sigma": 4.5,
    }


def train_models() -> dict[str, Any]:
    MODEL_DIR.mkdir(parents=True, exist_ok=True)

    rows = _rows()
    X, y = _matrix(rows)
    burn_model = _fit_ridge(X, y)
    fitted = _predict_in_sample(burn_model, X)
    anomaly_model = _fit_residual_model(y, fitted)

    metadata = {
        "burn_model": burn_model["model"],
        "anomaly_model": anomaly_model["model"],
        "training_rows": burn_model["training_rows"],
        "burn_model_mape": burn_model["mape"],
        "feature_names": FEATURE_NAMES,
    }

    BURN_MODEL_PATH.write_text(json.dumps(burn_model, indent=2), encoding="utf-8")
    ANOMALY_MODEL_PATH.write_text(json.dumps(anomaly_model, indent=2), encoding="utf-8")
    METADATA_PATH.write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    logger.info("trained ridge fuel burn model on %d rows, MAPE=%.4f", burn_model["training_rows"], burn_model["mape"])
    return metadata


if __name__ == "__main__":
    print(json.dumps(train_models(), indent=2))
