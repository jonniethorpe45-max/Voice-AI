# LOCAL_RUN.md

## Correct startup sequence

### Option A: Full stack via Docker (recommended)

`docker compose up --build -d` starts the **full stack** defined in `docker-compose.yml`:
- `app` (Node/Fastify API)
- `postgres`
- `redis`

In this mode, **you do NOT run `npm run dev` on host** unless you intentionally want a second API process.

API base URL (host):
- `http://localhost:3000/v1`

Health endpoint:
- `http://localhost:3000/health`
- expected response:
```json
{ "status": "ok", "service": "tax-deeds-backend" }
```

### Option B: Dependencies in Docker, API on host

Start only dependencies:
```bash
docker compose up -d postgres redis
```
Then run API on host:
```bash
cp .env.example .env
npm install
npm run prisma:generate
npm run prisma:deploy
npm run seed
npm run dev
```

In this mode, `npm run dev` **is required**.

---

## Expected healthy service list

When running full Docker stack:
- `taxdeeds_postgres` (healthy)
- `taxdeeds_redis` (running)
- `taxdeeds_app` (running)

Check:
```bash
docker compose ps
```

---

## Seeded login credentials (local dev)

From `prisma/seed.ts`:
- Admin
  - email: `admin@taxdeeds.local`
  - password: `Admin1234!`
- Reviewer
  - email: `reviewer@taxdeeds.local`
  - password: `Review1234!`

Local-only development credentials. Do not use in production.

---

## Health verification commands

### API
```bash
curl -s http://localhost:3000/health
```
Expected: JSON with `status: "ok"`.

### Postgres
```bash
docker compose exec postgres pg_isready -U user -d taxdeeds
```
Expected: accepting connections.

### Redis
```bash
docker compose exec redis redis-cli ping
```
Expected: `PONG`

### Seed/auth smoke test
```bash
curl -s -X POST http://localhost:3000/v1/auth/login   -H "Content-Type: application/json"   -d '{"email":"admin@taxdeeds.local","password":"Admin1234!"}'
```
Expected: `access_token`, `refresh_token`, `expires_at`.

---

## Common failure fixes

1. **`docker: command not found`**
   - Install Docker Desktop / Engine and Docker Compose plugin.

2. **Port 3000 already in use**
   - Stop existing process or change mapping in compose and Flutter base URL.

3. **Prisma migration errors**
   - Ensure `DATABASE_URL` points to running Postgres and run:
   ```bash
   npm run prisma:generate
   npm run prisma:deploy
   ```

4. **Seed fails due to schema mismatch**
   - Re-apply migrations, then run seed again:
   ```bash
   npm run prisma:deploy && npm run seed
   ```

5. **401 Unauthorized in Flutter**
   - Verify `Authorization: Bearer <access_token>` header is present.
   - Confirm token from `/v1/auth/login` and not expired.

6. **No dashboard/leads data**
   - Ensure seed ran successfully and login succeeded.

---

## Flutter connection

- Android emulator: `http://10.0.2.2:3000/v1`
- iOS simulator/Web: `http://localhost:3000/v1`

Set `useMockData = false` before end-to-end tests.
