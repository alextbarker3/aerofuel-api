# Model Card

## Purpose

The ML layer demonstrates how a fuel API can expose two simple predictive features:

1. predicted fuel burn
2. unusual burn variance flagging

The models are trained on synthetic data and are for demonstration only.

## Data

Source: `data/synthetic_flights.csv`

Features:

- aircraft profile
- distance
- payload
- taxi time
- wind component
- temperature

Target:

- actual fuel burn in kg

## Models

### Fuel burn prediction

- model: ridge regression
- output: predicted fuel burn in kg
- endpoint: `POST /ml/predict-fuel-burn`
- storage: JSON coefficients and feature scaling parameters

### Anomaly flagging

- model: robust residual model
- metric: actual burn versus model-estimated burn
- endpoint: `POST /ml/check-fuel-anomaly`
- storage: JSON residual centre and robust scale

The residual model is intentionally simple. It is auditable, deterministic and appropriate for a small API demonstration.

## Limitations

- synthetic data only
- no certified aircraft performance tables
- no live weather, NOTAM, dispatch, supplier-contract or military data
- not valid for operational flight planning
- not suitable for procurement decisions without verified supplier pricing

## Re-training

```bash
python scripts/bootstrap.py
```
