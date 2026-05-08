# Data Dictionary

## airports

| Field | Type | Description |
|---|---|---|
| icao_code | string | ICAO airport code |
| iata_code | string | IATA code, optional |
| name | string | Airport name |
| country | string | Country |
| latitude | float | Latitude |
| longitude | float | Longitude |
| timezone | string | IANA timezone |

## fuel_products

| Field | Type | Description |
|---|---|---|
| code | string | Product code, e.g. JET_A1 |
| name | string | Human-readable product name |
| density_kg_per_litre | float | Synthetic density assumption |
| emissions_factor_kg_co2_per_kg | float | Synthetic/default emissions factor |

## fuel_price_observations

| Field | Type | Description |
|---|---|---|
| airport_icao | string | ICAO airport code |
| fuel_type | string | Fuel product code |
| price | float | Price per unit |
| currency | string | ISO currency code |
| unit | string | Unit, e.g. LITRE |
| tax_status | string | Synthetic tax status |
| source_type | string | mock/live/synthetic provider type |
| source_name | string | Source label |
| confidence_score | float | 0-1 confidence indicator |
| observed_at | datetime | Timestamp |

## synthetic_flights

| Field | Type | Description |
|---|---|---|
| aircraft_profile | string | Synthetic aircraft category |
| origin | string | Origin ICAO |
| destination | string | Destination ICAO |
| distance_nm | float | Route distance in nautical miles |
| payload_kg | float | Payload assumption |
| taxi_minutes | float | Taxi time |
| wind_component_knots | float | Positive tailwind, negative headwind |
| temperature_c | float | Temperature |
| planned_burn_kg | float | Synthetic planned burn |
| actual_burn_kg | float | Synthetic actual burn |
| flight_date | date | Synthetic flight date |

## fuel_estimate_logs

| Field | Type | Description |
|---|---|---|
| created_at | datetime | API log timestamp |
| origin_icao | string | Origin ICAO |
| destination_icao | string | Destination ICAO |
| aircraft_profile | string | Synthetic profile name |
| estimated_total_fuel_kg | float | Total estimated fuel |
| estimated_cost | float/null | Optional cost estimate |
| predicted_burn_kg | float/null | Optional ML prediction |
| anomaly_flag | string | Stored anomaly flag |
| note | string/null | Log source label |
