from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

import httpx
import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

os.environ.setdefault("DATABASE_URL", "sqlite:///./test_aerofuel.db")

from app.db.database import Base, SessionLocal, engine
from app.db.seed import seed_database
from app.main import app


class SyncASGIClient:
    def __init__(self, app):
        self._transport = httpx.ASGITransport(app=app)

    def get(self, url: str, **kwargs):
        return asyncio.run(self._request("GET", url, **kwargs))

    def post(self, url: str, **kwargs):
        return asyncio.run(self._request("POST", url, **kwargs))

    async def _request(self, method: str, url: str, **kwargs):
        async with httpx.AsyncClient(transport=self._transport, base_url="http://testserver") as client:
            return await client.request(method, url, **kwargs)


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client():
    return SyncASGIClient(app)
