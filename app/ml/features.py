PROFILES = (
    "generic_light_aircraft",
    "generic_business_jet",
    "generic_transport_aircraft",
    "generic_heavy_transport",
)

FEATURE_NAMES = [
    "distance_nm",
    "payload_tonnes",
    "taxi_minutes",
    "headwind_knots",
    "tailwind_knots",
    "temperature_above_isa_c",
    "generic_light_aircraft",
    "generic_business_jet",
    "generic_transport_aircraft",
    "generic_heavy_transport",
    "distance_x_light",
    "distance_x_business",
    "distance_x_transport",
    "distance_x_heavy",
    "payload_distance",
]


def _profile_vector(profile: str) -> list[float]:
    selected = profile if profile in PROFILES else "generic_transport_aircraft"
    return [1.0 if item == selected else 0.0 for item in PROFILES]


def make_feature_row(
    aircraft_profile: str,
    distance_nm: float,
    payload_kg: float,
    taxi_minutes: float,
    wind_component_knots: float,
    temperature_c: float,
) -> list[float]:
    distance = float(distance_nm)
    payload_tonnes = float(payload_kg) / 1_000.0
    headwind = max(0.0, -float(wind_component_knots))
    tailwind = max(0.0, float(wind_component_knots))
    hot_day = max(0.0, float(temperature_c) - 15.0)
    profile = _profile_vector(aircraft_profile)

    return [
        distance,
        payload_tonnes,
        float(taxi_minutes),
        headwind,
        tailwind,
        hot_day,
        *profile,
        *(distance * value for value in profile),
        payload_tonnes * distance,
    ]
