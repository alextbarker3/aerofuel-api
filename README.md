# AeroFuel API

AeroFuel API is a small aviation fuel‑intelligence service I’m building for mission‑planning and flight‑ops style workflows.  
It exposes endpoints for fuel prices, route and cost estimates, uplift comparisons, and some lightweight ML around fuel burn and anomalies.

This repo ships with synthetic data only.  
It is not connected to RAF, MOD, STARS, certified flight‑planning tools, or any live operational systems, and it is not valid for real‑world flight planning.

## What it can do

- Look up airport fuel prices from a local cache
- Optionally refresh live prices from an approved HTTPS supplier endpoint
- Estimate route fuel requirements
- Estimate fuel cost for a route or scenario
- Compare uplift options between airfields
- Predict fuel burn using a small ridge‑regression model
- Flag unusual fuel burn using a simple residual‑based anomaly check
- Export data as JSON or CSV for BI and reporting tools

## How it’s put together

```text
Planning / ops / BI client
 │  HTTP / JSON / CSV
 ▼
AeroFuel API
 ├── FastAPI + Pydantic contracts
 ├── Supplier adapter for live fuel prices
 ├── Fuel estimate and cost services
 ├── Lightweight ML inference
 └── SQLAlchemy data access
 ▼
SQLite locally / PostgreSQL in deployment
```

The live‑fuel path is deliberately narrow: outbound HTTPS only to allow‑listed supplier hosts, API credentials coming from environment variables, local caching, no inbound callbacks, and no embedded secrets.

## Stack

- FastAPI
- Pydantic
- SQLAlchemy
- SQLite locally, PostgreSQL‑ready
- httpx for outbound supplier calls
- NumPy for model work
- pytest for tests
- Docker for packaging and deployment

## Getting started

Clone the repo and set up a virtual environment:

```bash
git clone https://github.com/YOUR_USERNAME/aerofuel-api.git
cd aerofuel-api

python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

pip install -r requirements.txt
python scripts/bootstrap.py
uvicorn app.main:app --reload
```

Then open the interactive docs:

```text
http://127.0.0.1:8000/docs
```

You should see the OpenAPI/Swagger UI with all endpoints listed and ready to try.

## Main endpoints

| Capability              | Endpoint                                   |
|-------------------------|--------------------------------------------|
| Health                  | `GET /health`                              |
| Integration status      | `GET /integrations/fuel-data/status`       |
| List airports           | `GET /airports`                            |
| Airport fuel prices     | `GET /airports/{icao}/fuel-prices`         |
| Refresh live fuel prices| `POST /airports/{icao}/fuel-prices/refresh`|
| Route fuel estimate     | `POST /fuel/estimate`                      |
| Cost estimate           | `POST /fuel/cost-estimate`                 |
| Uplift comparison       | `POST /fuel/compare-uplift`                |
| Fuel burn prediction    | `POST /ml/predict-fuel-burn`               |
| Anomaly check           | `POST /ml/check-fuel-anomaly`              |

---

If you’re using this for experiments, feel free to raise issues or open PRs with ideas for new endpoints, models, or checks.
