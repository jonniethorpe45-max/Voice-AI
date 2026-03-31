# Tax Deeds Backend (Fastify + Prisma)

Production-ready REST API backend for the Flutter Tax Deeds admin app.

## Stack

- Node.js 20 + TypeScript 5
- Fastify 4
- Prisma 5 + PostgreSQL 15
- BullMQ + Redis 7
- Zod validation
- Axios outbound integrations
- Vitest tests
- Docker + docker-compose

## Startup modes

### Full stack with Docker (app + postgres + redis)

```bash
cp .env.example .env
docker compose up --build -d
```

In this mode, do **not** run `npm run dev` on host unless you intentionally want a second API process.

API base URL:
- `http://localhost:3000/v1`

Health endpoint:
- `http://localhost:3000/health`
- response:
```json
{ "status": "ok", "service": "tax-deeds-backend" }
```

### Dependencies only (postgres + redis), API on host

```bash
docker compose up -d postgres redis
cp .env.example .env
npm install
npm run prisma:generate
npm run prisma:deploy
npm run seed
npm run dev
```

In this mode, `npm run dev` is required.

## Seeded local credentials

- Admin: `admin@taxdeeds.local` / `Admin1234!`
- Reviewer: `reviewer@taxdeeds.local` / `Review1234!`

## Flutter base URL

- Android emulator: `http://10.0.2.2:3000/v1`
- iOS simulator/Web: `http://localhost:3000/v1`

Set `useMockData = false` for live backend testing.

## Contract tooling

```bash
npm run contract:generate
npm run contract:check
```

- `contract_report.json` is deterministic and CI-validated.
- CI workflow: `.github/workflows/contract-check.yml`

## Key endpoints

- `POST /v1/auth/login`
- `POST /v1/auth/logout`
- `POST /v1/auth/refresh`
- `GET /v1/leads`
- `GET /v1/leads/:id`
- `POST /v1/leads/:id/approve`
- `POST /v1/leads/:id/reject`
- `POST /v1/leads/:id/hold`
- `POST /v1/leads/:id/clear-legal-review`
- `POST /v1/leads/:id/notes`
- `GET /v1/letters/queue`
- `GET /v1/dashboard/stats`
- `GET /v1/notifications`
- `POST /v1/notifications/:id/read`
- `POST /v1/notifications/read-all`
- `GET /v1/tracking`
- `GET /v1/tracking/:id`
- `POST /v1/webhooks/lob`
