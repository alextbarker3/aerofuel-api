def test_fuel_estimate(client):
    response = client.post("/fuel/estimate", json={
        "aircraft_profile": "generic_transport_aircraft",
        "origin": "EGTK",
        "destination": "EGSS",
        "distance_nm": 65,
        "payload_kg": 800,
        "taxi_minutes": 12,
        "wind_component_knots": -10,
        "temperature_c": 14,
    })
    assert response.status_code == 200
    body = response.json()
    assert body["fuel_required_kg"]["total"] > 0
    assert body["estimated_co2_kg"] > 0


def test_fuel_estimate_is_monotone_in_distance(client):
    """Trip fuel must grow strictly with distance, all else equal."""
    base = {
        "aircraft_profile": "generic_transport_aircraft",
        "origin": "EGTK",
        "destination": "EGSS",
        "payload_kg": 800,
        "taxi_minutes": 12,
        "wind_component_knots": 0,
        "temperature_c": 15,
    }
    short = client.post("/fuel/estimate", json={**base, "distance_nm": 100}).json()
    long = client.post("/fuel/estimate", json={**base, "distance_nm": 500}).json()
    assert long["fuel_required_kg"]["trip"] > short["fuel_required_kg"]["trip"]
    assert long["fuel_required_kg"]["total"] > short["fuel_required_kg"]["total"]


def test_cost_estimate(client):
    response = client.post("/fuel/cost-estimate", json={
        "airport_icao": "EGTK",
        "fuel_type": "JET_A1",
        "uplift_litres": 3000,
    })
    assert response.status_code == 200
    assert response.json()["estimated_cost"] > 0


def test_compare_uplift(client):
    response = client.post("/fuel/compare-uplift", json={
        "origin": "EGTK",
        "destination": "EGSS",
        "fuel_type": "JET_A1",
        "extra_uplift_litres": 800,
        "extra_burn_cost": 35,
    })
    assert response.status_code == 200
    assert response.json()["suggested_option"] in {"tanker_at_origin", "uplift_at_destination", "neutral"}


def test_compare_uplift_sign_correctness(client):
    """If origin price exceeds destination price by enough to overcome the
    extra-burn penalty, the recommendation must be to uplift at destination."""
    # In the seed data EGTK = 1.52 GBP/L, EGSS = 1.78 GBP/L, so swapping
    # origin/destination puts the expensive airport first.
    response = client.post("/fuel/compare-uplift", json={
        "origin": "EGSS",
        "destination": "EGTK",
        "fuel_type": "JET_A1",
        "extra_uplift_litres": 1000,
        "extra_burn_cost": 0,
    }).json()
    assert response["gross_saving"] < 0
    assert response["suggested_option"] == "uplift_at_destination"
