from datetime import datetime

from app.integrations.fuel_price_provider import NormalizedFuelPrice
from app.services.fuel_price_service import refresh_external_fuel_prices


def test_fuel_data_status_endpoint(client):
    response = client.get("/integrations/fuel-data/status")
    assert response.status_code == 200
    payload = response.json()
    assert payload["mode"] == "local"
    assert payload["live_fuel_enabled"] is False
    assert payload["transport"] == "outbound_https_only"


def test_refresh_endpoint_caches_provider_rows(client, monkeypatch):
    async def fake_fetch(self, icao: str):
        return [
            NormalizedFuelPrice(
                airport_icao=icao,
                fuel_type="JET_A1",
                price=1.99,
                currency="GBP",
                unit="LITRE",
                tax_status="EX_VAT",
                source_type="external_provider",
                source_name="test_supplier",
                source_url="https://fuel.example.test/airports/EGTK/fuel-prices",
                confidence_score=0.91,
                observed_at=datetime.fromisoformat("2026-05-07T10:00:00"),
            )
        ]

    monkeypatch.setattr(
        "app.services.fuel_price_service.ExternalFuelPriceProvider.fetch_airport_prices",
        fake_fetch,
    )

    response = client.post("/airports/EGTK/fuel-prices/refresh")
    assert response.status_code == 200
    payload = response.json()
    assert payload["airport_icao"] == "EGTK"
    assert payload["rows_cached"] == 1
    assert payload["fuel_prices"][0]["source_name"] == "test_supplier"
