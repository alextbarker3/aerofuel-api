# AeroFuel API

AeroFuel API is a compact aviation fuel-intelligence service. It exposes fuel price, fuel estimate, uplift comparison and lightweight ML endpoints for mission-planning, flight-operations, procurement, BI or reporting clients.

The repository ships with synthetic data only. It is not connected to RAF, MOD, STARS, certified flight-planning tools or live operational systems. It is not valid for operational flight planning.

## Capabilities

- Airport fuel price lookup from local cache
- Optional live refresh from an approved HTTPS supplier endpoint
- Route fuel estimate
- Fuel cost estimate
- Uplift cost comparison
- Fuel burn prediction using a small ridge-regression model
- Fuel burn variance flagging using a robust residual model
- JSON/CSV export for BI tools

## Architecture

```text
Planning / ops / BI client
        │  HTTP / JSON / CSV
        ▼
AeroFuel API
        ├── FastAPI + Pydantic contracts
        ├── supplier adapter for live fuel prices
        ├── fuel estimate and cost services
        ├── lightweight ML inference
        └── SQLAlchemy data access
        ▼
SQLite locally / PostgreSQL in deployment
```

The live-fuel path is deliberately narrow: outbound HTTPS to allowlisted supplier hosts, API credentials through environment variables, local caching, no inbound supplier callbacks and no embedded secrets.

## Stack

- FastAPI
- Pydantic
- SQLAlchemy
- SQLite locally, PostgreSQL-ready
- httpx for outbound supplier calls
- NumPy for model training
- pytest
- Docker

## Quick start

```bash
git clone https://github.com/YOUR_USERNAME/aerofuel-api.git
cd aerofuel-api
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python scripts/bootstrap.py
uvicorn app.main:app --reload
```

Open:

```text
http://127.0.0.1:8000/docs
```

## Main endpoints

| Capability | Endpoint |
|---|---|
| Health | `GET /health` |
| Integration status | `GET /integrations/fuel-data/status` |
| List airports | `GET /airports` |
| Airport fuel prices | `GET /airports/{icao}/fuel-prices` |
| Refresh live fuel prices | `POST /airports/{icao}/fuel-prices/refresh` |
| Route fuel estimate | `POST /fuel/estimate` |
| Cost estimate | `POST /fuel/cost-estimate` |
| Uplift comparison | `POST /fuel/compare-uplift` |
| Fuel burn prediction | `POST /ml/predict-fuel-burn` |
| Anomaly check | `POST /ml/check-fuel-anomaly` |
| BI export | `GET /exports/estimates` |

## Live fuel provider configuration

The default mode is local synthetic data. To enable a supplier adapter:

```text
FUEL_DATA_MODE=hybrid
EXTERNAL_FUEL_API_BASE_URL=https://fuel-provider.example.com
EXTERNAL_FUEL_API_PATH_TEMPLATE=/airports/{icao}/fuel-prices
EXTERNAL_FUEL_API_KEY=provider-secret
EXTERNAL_FUEL_API_KEY_HEADER=X-API-Key
EXTERNAL_FUEL_ALLOWED_HOSTS=fuel-provider.example.com
EXTERNAL_FUEL_PROVIDER_NAME=approved_fuel_provider
```

Then refresh cached prices:

```bash
curl -X POST http://127.0.0.1:8000/airports/EGTK/fuel-prices/refresh \
  -H "X-API-Key: your-aerofuel-key"
```

Accepted supplier payload:

```json
{
  "fuel_prices": [
    {
      "fuel_type": "JET_A1",
      "price": 1.52,
      "currency": "GBP",
      "unit": "LITRE",
      "tax_status": "EX_VAT",
      "source_name": "approved_fuel_provider",
      "updated_at": "2026-05-07T10:00:00Z"
    }
  ]
}
```

A direct list of price objects is also accepted. Supplier responses are normalised before local caching.

## Protected-network assumptions

For enterprise or defence-style networks, AeroFuel assumes authorised outbound HTTPS through existing network controls. It does not attempt to bypass firewalls, tunnel traffic, disable certificate verification or create inbound supplier connections. Supplier domains, certificates, logs, hosting and secrets handling should be approved by the environment owner.

## Example request

```bash
curl -X POST http://127.0.0.1:8000/fuel/estimate \
  -H "Content-Type: application/json" \
  -d '{
    "aircraft_profile": "generic_transport_aircraft",
    "origin": "EGTK",
    "destination": "EGSS",
    "distance_nm": 65,
    "payload_kg": 800,
    "taxi_minutes": 12,
    "wind_component_knots": -10,
    "temperature_c": 14
  }'
```

## API key

For local development, the API is open by default. To protect a deployment:

```bash
AEROFUEL_API_KEY=your-secret-key
```

Then send:

```http
X-API-Key: your-secret-key
```

## Machine learning

The ML layer is intentionally small and auditable.

1. A ridge-regression model predicts fuel burn from distance, payload, taxi time, wind, temperature and aircraft profile.
2. A robust residual model flags materially unusual burn variance.

Models are trained on synthetic data by:

```bash
python scripts/bootstrap.py
```

The generated model files are JSON, not opaque binaries.

## BI export

```http
GET /exports/estimates?format=json
GET /exports/estimates?format=csv
```

## Project structure

```text
app/
  api/           FastAPI route modules
  db/            SQLAlchemy models and session setup
  integrations/  external fuel provider adapter
  ml/            training and inference modules
  schemas/       Pydantic request/response models
  services/      domain logic
data/            synthetic source data
docs/            API examples, architecture, model card, integration notes
examples/        sample request payloads
scripts/         bootstrap and OpenAPI generation
tests/           pytest suite
```

## Test

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest -q
```

## Positioning

AeroFuel API is a clean engineering portfolio project: a small aviation fuel plug-in with typed API contracts, a live-provider adapter pattern, synthetic data, auditable ML, OpenAPI docs, tests and deployment files.
"# aerofuel-api" 
