from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import routes_airports, routes_exports, routes_fuel, routes_health, routes_integrations, routes_ml
from app.config import get_settings
from app.db.database import SessionLocal
from app.db.seed import create_tables, seed_database


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()
    yield


settings = get_settings()

app = FastAPI(
    title="AeroFuel API",
    version=settings.version,
    description="Aviation fuel intelligence API. Synthetic data; demonstration use only.",
    contact={"name": "AeroFuel API"},
    license_info={"name": "MIT"},
    lifespan=lifespan,
)

# allow_credentials must be False when origins is "*". The service authenticates
# via the X-API-Key header, which CORS does not treat as a credential.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.parsed_cors_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "X-API-Key"],
)

app.include_router(routes_health.router)
app.include_router(routes_airports.router)
app.include_router(routes_fuel.router)
app.include_router(routes_ml.router)
app.include_router(routes_exports.router)
app.include_router(routes_integrations.router)
