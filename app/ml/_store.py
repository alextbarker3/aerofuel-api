"""Shared model-artifact paths and lazy training hook for the ML layer."""
from __future__ import annotations

import json
from pathlib import Path

MODEL_DIR = Path(__file__).resolve().parent / "models"
BURN_MODEL_PATH = MODEL_DIR / "fuel_burn_ridge.json"
ANOMALY_MODEL_PATH = MODEL_DIR / "fuel_anomaly_residual.json"
METADATA_PATH = MODEL_DIR / "model_metadata.json"


def ensure_models() -> None:
    """Train models on first use if no artifacts are on disk yet."""
    if BURN_MODEL_PATH.exists() and ANOMALY_MODEL_PATH.exists() and METADATA_PATH.exists():
        return
    from app.ml.train import train_models

    train_models()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))
