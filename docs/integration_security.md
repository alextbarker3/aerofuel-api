# Integration and Security Notes

AeroFuel API is designed as a small fuel-data plug-in. It can be called by an authorised planning, operations or BI system, and it can refresh cached fuel prices from an approved external supplier.

## Network pattern

Recommended pattern:

```text
Client system / BI tool
        ↓ internal HTTP(S)
AeroFuel API
        ↓ outbound HTTPS only
Approved fuel-price supplier
```

The API does not require inbound supplier callbacks, tunnelling, reverse shells, custom VPN logic, or firewall bypasses.

## Controls included in the project

- API key protection for AeroFuel endpoints via `AEROFUEL_API_KEY`.
- External provider calls use HTTPS only.
- External provider hosts can be allowlisted with `EXTERNAL_FUEL_ALLOWED_HOSTS`.
- Supplier credentials are read from environment variables.
- Supplier data is normalised and cached locally before use.
- Provider failures return controlled 502/503 responses.
- The public repository contains no live credentials and no operational data.

## Configuration example

```text
FUEL_DATA_MODE=hybrid
EXTERNAL_FUEL_API_BASE_URL=https://fuel-provider.example.com
EXTERNAL_FUEL_API_PATH_TEMPLATE=/airports/{icao}/fuel-prices
EXTERNAL_FUEL_API_KEY=provider-secret
EXTERNAL_FUEL_API_KEY_HEADER=X-API-Key
EXTERNAL_FUEL_ALLOWED_HOSTS=fuel-provider.example.com
```

## Protected-network deployment notes

For protected enterprise or defence-style environments, use the existing approved internet egress route and proxy policy. Do not build bypass paths into the plug-in. In practice, the environment owner would normally approve specific supplier domains, certificate trust, logging, hosting, secrets handling and client-system integration.

Keep the plug-in modest: it should enrich authorised planning or reporting workflows with fuel-price data. It should not claim to integrate with any classified, restricted, or operational system unless that integration has been formally authorised and accredited.
