from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal, InvalidOperation
from urllib.parse import urljoin, urlparse

import httpx
from fastapi import HTTPException, status

from app.config import Settings


@dataclass(frozen=True)
class NormalizedFuelPrice:
    airport_icao: str
    fuel_type: str
    price: float
    currency: str
    unit: str
    tax_status: str
    source_type: str
    source_name: str
    source_url: str | None
    confidence_score: float
    observed_at: datetime


class ExternalFuelPriceProvider:
    """Fetches airport fuel prices from an approved external HTTP provider.

    The provider response is deliberately normalised into AeroFuel's internal
    schema. This keeps mission-planning, BI and reporting integrations stable
    even when the upstream supplier changes field names.
    """

    def __init__(self, settings: Settings):
        self.settings = settings

    @property
    def configured(self) -> bool:
        return bool(self.settings.external_fuel_api_base_url)

    async def fetch_airport_prices(self, icao: str) -> list[NormalizedFuelPrice]:
        if not self.configured:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="No external fuel price provider is configured",
            )

        url = self._build_url(icao)
        self._validate_url(url)

        headers = {"Accept": "application/json", "User-Agent": "aerofuel-api/0.3"}
        if self.settings.external_fuel_api_key:
            headers[self.settings.external_fuel_api_key_header] = self.settings.external_fuel_api_key

        try:
            async with httpx.AsyncClient(timeout=self.settings.external_fuel_api_timeout_seconds) as client:
                response = await client.get(url, headers=headers)
                response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Fuel provider returned HTTP {exc.response.status_code}",
            ) from exc
        except httpx.RequestError as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Fuel provider request failed",
            ) from exc

        return self._normalise_payload(response.json(), icao=icao.upper(), source_url=url)

    def _build_url(self, icao: str) -> str:
        base_url = self.settings.external_fuel_api_base_url or ""
        path = self.settings.external_fuel_api_path_template.format(icao=icao.upper())
        return urljoin(base_url.rstrip("/") + "/", path.lstrip("/"))

    def _validate_url(self, url: str) -> None:
        parsed = urlparse(url)
        if parsed.scheme != "https":
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="External fuel provider URL must use HTTPS",
            )

        hostname = parsed.hostname or ""
        allowed_hosts = self.settings.parsed_external_fuel_allowed_hosts
        if allowed_hosts and hostname not in allowed_hosts:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="External fuel provider host is not allowlisted",
            )

    def _normalise_payload(self, payload: object, *, icao: str, source_url: str) -> list[NormalizedFuelPrice]:
        rows: list[dict]
        if isinstance(payload, dict):
            raw_rows = payload.get("fuel_prices") or payload.get("prices") or []
            if not isinstance(raw_rows, list):
                raise self._bad_payload("fuel_prices must be a list")
            rows = raw_rows
        elif isinstance(payload, list):
            rows = payload
        else:
            raise self._bad_payload("payload must be an object or list")

        normalised = [self._normalise_row(row, icao=icao, source_url=source_url) for row in rows if isinstance(row, dict)]
        if not normalised:
            raise self._bad_payload("provider returned no usable fuel prices")
        return normalised

    def _normalise_row(self, row: dict, *, icao: str, source_url: str) -> NormalizedFuelPrice:
        fuel_type = str(row.get("fuel_type") or row.get("product") or row.get("code") or "JET_A1").upper()
        currency = str(row.get("currency") or "GBP").upper()
        unit = str(row.get("unit") or "LITRE").upper()
        tax_status = str(row.get("tax_status") or row.get("tax") or "UNKNOWN").upper()
        source_name = str(row.get("source_name") or self.settings.external_fuel_provider_name)
        source_type = str(row.get("source_type") or "external_provider")
        confidence_score = _bounded_float(row.get("confidence_score", 0.85), default=0.85, lower=0.0, upper=1.0)
        observed_at = _parse_datetime(row.get("updated_at") or row.get("observed_at"))
        price = _positive_float(row.get("price"))

        return NormalizedFuelPrice(
            airport_icao=icao,
            fuel_type=fuel_type,
            price=price,
            currency=currency,
            unit=unit,
            tax_status=tax_status,
            source_type=source_type,
            source_name=source_name,
            source_url=str(row.get("source_url") or source_url),
            confidence_score=confidence_score,
            observed_at=observed_at,
        )

    @staticmethod
    def _bad_payload(detail: str) -> HTTPException:
        return HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"Invalid fuel provider payload: {detail}")


def _positive_float(value: object) -> float:
    try:
        parsed = Decimal(str(value))
    except (InvalidOperation, TypeError):
        raise ExternalFuelPriceProvider._bad_payload("price must be numeric")
    if parsed <= 0:
        raise ExternalFuelPriceProvider._bad_payload("price must be positive")
    return float(parsed)


def _bounded_float(value: object, *, default: float, lower: float, upper: float) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return default
    return max(lower, min(upper, parsed))


def _parse_datetime(value: object) -> datetime:
    if not value:
        return datetime.now(UTC).replace(tzinfo=None)
    if isinstance(value, datetime):
        return value.replace(tzinfo=None)
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00")).replace(tzinfo=None)
    except ValueError:
        return datetime.now(UTC).replace(tzinfo=None)
