"""Minimal Python client example for AeroFuel API."""

import httpx

BASE_URL = "http://127.0.0.1:8000"
API_KEY = None  # Set if AEROFUEL_API_KEY is configured on the server.

headers = {"Content-Type": "application/json"}
if API_KEY:
    headers["X-API-Key"] = API_KEY

payload = {
    "aircraft_profile": "generic_transport_aircraft",
    "origin": "EGTK",
    "destination": "EGSS",
    "distance_nm": 65,
    "payload_kg": 800,
    "taxi_minutes": 12,
    "wind_component_knots": -10,
    "temperature_c": 14,
}

with httpx.Client(timeout=20) as client:
    response = client.post(f"{BASE_URL}/fuel/estimate", json=payload, headers=headers)
    response.raise_for_status()
    print(response.json())
