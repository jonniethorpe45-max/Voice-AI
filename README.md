# Surplus Recovery Ops Backend (FastAPI)

Production-ready backend for the Surplus Recovery Ops Flutter admin app.

## Stack

- FastAPI
- PostgreSQL
- SQLAlchemy + Alembic
- Redis + RQ background jobs
- Docker Compose local environment

## Features Implemented

- Admin auth (JWT access + refresh)
- County config for exactly:
  - CA_LA
  - CA_ORANGE
  - CA_EL_DORADO
  - CA_TULARE
  - FL_LEE
  - FL_BREVARD
- Leads lifecycle and notes
- Dashboard aggregates
- County ingestion engine + adapters
- Lead normalization, dedupe hash, quality flags
- Contact enrichment abstraction (mailing address gate)
- Lob integration layer:
  - address verify/standardize
  - preview letter
  - approve/reject/hold
  - send and tracking sync
- Tracking timeline
- Response intake:
  - inbound email webhook
  - Twilio webhook
  - manual operator logging
- Notifications
- Audit logging
- API docs at `/docs`

## Quick Start (One command)

1. Copy env:

```bash
cp .env.example .env
```

2. Start everything:

```bash
docker compose up --build
```

3. Run migrations:

```bash
docker compose exec api alembic upgrade head
```

4. Seed data:

```bash
docker compose exec api python -m scripts.seed
```

API: `http://localhost:8000`

Docs: `http://localhost:8000/docs`

## Auth

Default seeded admin comes from `.env`:

- `SEED_ADMIN_EMAIL`
- `SEED_ADMIN_PASSWORD`

Login endpoint:

`POST /api/v1/auth/login`

## Testing

Run county adapter fixture tests:

```bash
pytest -q
```

## Notes on Flutter Contract

This backend includes all endpoint groups and payload structures required in the task statement:

- auth
- dashboard
- leads list/detail/notes/legal-review clear
- letters queue/preview/approve/reject/hold/send
- tracking list/detail/manual create
- notifications
- response intake and webhooks

If you provide the exact `api_service.dart` + model files, we can do a strict final naming alignment pass in minutes.
