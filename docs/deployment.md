# Deployment

## Local

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts/bootstrap.py
uvicorn app.main:app --reload
```

## Docker

```bash
docker compose up --build
```

## Public hosting

Suitable options:

- Render Web Service
- Railway
- Fly.io
- AWS ECS/App Runner
- Azure Container Apps

Set the following variables in production:

```text
DATABASE_URL=postgresql+psycopg://user:password@host:5432/aerofuel
AEROFUEL_API_KEY=your-secret-key
ENVIRONMENT=production
CORS_ORIGINS=https://yourdomain.com
```

Install a PostgreSQL driver such as `psycopg[binary]` if deploying against PostgreSQL.

## Notes

- For a public demo, set `AEROFUEL_API_KEY`.
- Use PostgreSQL for production-style deployment.
- Configure a real supplier adapter before using live fuel data.
- Add Alembic migrations if the schema will evolve.
