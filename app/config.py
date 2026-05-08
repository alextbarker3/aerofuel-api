from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "AeroFuel API"
    version: str = "0.4.0"
    environment: str = Field(default="local", alias="ENVIRONMENT")
    database_url: str = Field(default="sqlite:///./aerofuel.db", alias="DATABASE_URL")
    aerofuel_api_key: str | None = Field(default=None, alias="AEROFUEL_API_KEY")
    cors_origins: str = Field(default="*", alias="CORS_ORIGINS")

    fuel_data_mode: str = Field(default="local", alias="FUEL_DATA_MODE")  # local | external | hybrid
    external_fuel_api_base_url: str | None = Field(default=None, alias="EXTERNAL_FUEL_API_BASE_URL")
    external_fuel_api_path_template: str = Field(
        default="/airports/{icao}/fuel-prices",
        alias="EXTERNAL_FUEL_API_PATH_TEMPLATE",
    )
    external_fuel_api_key: str | None = Field(default=None, alias="EXTERNAL_FUEL_API_KEY")
    external_fuel_api_key_header: str = Field(default="X-API-Key", alias="EXTERNAL_FUEL_API_KEY_HEADER")
    external_fuel_api_timeout_seconds: float = Field(default=8.0, alias="EXTERNAL_FUEL_API_TIMEOUT_SECONDS")
    external_fuel_allowed_hosts: str = Field(default="", alias="EXTERNAL_FUEL_ALLOWED_HOSTS")
    external_fuel_provider_name: str = Field(default="external_fuel_provider", alias="EXTERNAL_FUEL_PROVIDER_NAME")

    @property
    def live_fuel_enabled(self) -> bool:
        return self.fuel_data_mode.lower() in {"external", "hybrid"} and bool(self.external_fuel_api_base_url)

    @property
    def parsed_cors_origins(self) -> list[str]:
        if self.cors_origins.strip() == "*":
            return ["*"]
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def parsed_external_fuel_allowed_hosts(self) -> list[str]:
        return [host.strip().lower() for host in self.external_fuel_allowed_hosts.split(",") if host.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
