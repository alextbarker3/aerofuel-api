# AeroFuel API

AeroFuel API is a small aviation fuel‑intelligence service I’m building for mission‑planning and flight‑ops style workflows.  
It exposes endpoints for fuel prices, route and cost estimates, uplift comparisons, and some lightweight ML around fuel burn and anomalies.

This repo ships with synthetic data only.  
It is not connected to RAF, MOD, STARS, certified flight‑planning tools, or any live operational systems, and it is not valid for real‑world flight planning.

## Why I built this (portfolio context)

This project is aimed at showcasing how I would approach a production‑style API in a defence / aviation context:

- Clear contracts and typed models
- External integration over HTTPS with proper isolation
- Basic ML used in a constrained, auditable way
- Tests, Docker packaging, and a structure that could grow into a larger service

If you’re reviewing this as a prospective employer, the code is meant to be read: comments are sparse but intentional, and the modules are split to make the design choices obvious.

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

| Capability               | Endpoint                                     |
|--------------------------|----------------------------------------------|
| Health                   | `GET /health`                                |
| Integration status       | `GET /integrations/fuel-data/status`         |
| List airports            | `GET /airports`                              |
| Airport fuel prices      | `GET /airports/{icao}/fuel-prices`          |
| Refresh live fuel prices | `POST /airports/{icao}/fuel-prices/refresh` |
| Route fuel estimate      | `POST /fuel/estimate`                        |
| Cost estimate            | `POST /fuel/cost-estimate`                   |
| Uplift comparison        | `POST /fuel/compare-uplift`                  |
| Fuel burn prediction     | `POST /ml/predict-fuel-burn`                 |
| Anomaly check            | `POST /ml/check-fuel-anomaly`                |

---

If you’re looking at this as part of an application and want to know how I’d extend it (e.g. auth, observability, or more formal ML), I’ve added some notes in the issues section.
