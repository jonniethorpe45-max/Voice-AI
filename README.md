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

## One-command local startup

```bash
cp .env.example .env && docker compose up --build
```

API: `http://localhost:3000/v1`

Android emulator base URL: `http://10.0.2.2:3000/v1`

## Local setup without Docker

```bash
npm install
npm run prisma:generate
npm run prisma:migrate
npm run seed
npm run dev
```

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
- `GET /v1/dashboard/stats`
- `GET /v1/notifications`
- `POST /v1/notifications/:id/read`
- `POST /v1/notifications/read-all`
- `POST /v1/webhooks/lob`
