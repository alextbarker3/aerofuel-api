# API Examples

## Integration status

```bash
curl http://127.0.0.1:8000/integrations/fuel-data/status
```

## Get cached airport fuel prices

```bash
curl http://127.0.0.1:8000/airports/EGTK/fuel-prices
```

## Refresh live fuel prices from configured supplier

```bash
curl -X POST http://127.0.0.1:8000/airports/EGTK/fuel-prices/refresh \
  -H "X-API-Key: your-aerofuel-key"
```

## Fuel estimate

```bash
curl -X POST http://127.0.0.1:8000/fuel/estimate \
  -H "Content-Type: application/json" \
  -d @examples/fuel_estimate.json
```

## Cost estimate

```bash
curl -X POST http://127.0.0.1:8000/fuel/cost-estimate \
  -H "Content-Type: application/json" \
  -d @examples/cost_estimate.json
```

## ML prediction

```bash
curl -X POST http://127.0.0.1:8000/ml/predict-fuel-burn \
  -H "Content-Type: application/json" \
  -d @examples/predict_fuel_burn.json
```

## Anomaly check

```bash
curl -X POST http://127.0.0.1:8000/ml/check-fuel-anomaly \
  -H "Content-Type: application/json" \
  -d @examples/check_anomaly.json
```

## BI export

```bash
curl "http://127.0.0.1:8000/exports/estimates?format=csv"
```
