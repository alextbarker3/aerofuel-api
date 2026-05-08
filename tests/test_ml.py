def test_ml_predict_fuel_burn(client):
    response = client.post(
        "/ml/predict-fuel-burn",
        json={
            "aircraft_profile": "generic_transport_aircraft",
            "distance_nm": 65,
            "payload_kg": 800,
            "taxi_minutes": 12,
            "wind_component_knots": -10,
            "temperature_c": 14,
        },
    )
    assert response.status_code == 200
    assert response.json()["predicted_fuel_burn_kg"] > 0


def test_ml_check_anomaly(client):
    response = client.post(
        "/ml/check-fuel-anomaly",
        json={
            "aircraft_profile": "generic_transport_aircraft",
            "actual_burn_kg": 1170,
            "distance_nm": 65,
            "payload_kg": 800,
            "taxi_minutes": 18,
            "wind_component_knots": -10,
            "temperature_c": 14,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["expected_burn_kg"] > 0
    assert data["severity"] in {"normal", "low", "medium", "high"}
