# Architecture

AeroFuel API is deliberately small: a fuel-intelligence service that another planning, operations or BI tool can call.

```text
Client system
  └─ HTTP / JSON / CSV
      └─ FastAPI application
          ├─ route modules
          ├─ Pydantic schemas
          ├─ service layer
          ├─ provider adapter layer
          ├─ SQLAlchemy data access
          └─ lightweight ML inference
```

## API layer

FastAPI exposes typed endpoints. OpenAPI/Swagger docs are available at `/docs`.

## Provider adapter layer

`app/integrations/fuel_price_provider.py` contains the outbound live-fuel adapter. It pulls airport fuel prices from a configured HTTPS supplier endpoint, validates the supplier host, normalises the payload and caches accepted rows.

The adapter is intentionally narrow:

- outbound HTTPS only
- optional supplier API-key header
- supplier host allowlist
- no inbound callbacks
- no embedded credentials

## Service layer

Route modules stay thin. Calculation, price lookup, provider refresh, uplift comparison and export logic sit in service modules.

## Data layer

SQLAlchemy supports SQLite for local use and PostgreSQL for deployment. Supplier fuel prices are cached in `fuel_price_observations`. Seed data is synthetic.

## ML layer

The ML layer is an enrichment layer only:

- fuel burn prediction with ridge regression
- anomaly support with a robust residual model

Models are trained from synthetic CSV data and persisted as JSON for transparency.

## Integration pattern

```text
Existing planning or reporting system
        ↓
AeroFuel API
        ↓
JSON response, CSV export, or BI connector
```

The API is not a certified flight-planning tool and does not contain operational aircraft performance data.
