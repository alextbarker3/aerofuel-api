def test_airport_fuel_prices(client):
    response = client.get("/airports/EGTK/fuel-prices")
    assert response.status_code == 200
    payload = response.json()
    assert payload["airport_icao"] == "EGTK"
    assert len(payload["fuel_prices"]) >= 1
