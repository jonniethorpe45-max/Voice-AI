# VocalFit AI — Intelligent Vocal Transformation Engine

Production-ready MVP for a **song-aware vocal resynthesis app** that transforms user singing while preserving emotion, phrasing, and natural character.

## What is included

- FastAPI backend with required endpoints:
  - `POST /upload`
  - `POST /process`
  - `GET /status/{job_id}`
  - `GET /results/{job_id}`
- Redis-backed async queue with CPU/GPU worker pools
- Modular audio pipeline:
  - Source separation (Demucs best effort + fallback)
  - Analysis (F0, note segmentation, phrasing, breath events, loudness, key/chords)
  - Performance encoding
  - SVC-style timbre enhancement
  - Soft musical pitch guidance (not hard auto-tune)
  - Song-aware section adaptation
  - Mixing + 5 output variations
  - Song Fit Score ranking + automatic best variation selection
- Dockerized deployment for API + CPU worker + GPU worker + Redis
- Flutter mobile/web frontend scaffold with required screens
- Sample audio generation utility and API docs

## Repository structure

```text
/frontend                Flutter app (mobile-first + web-capable)
/backend                 FastAPI app, worker, pipeline modules
/models                  Model registry placeholders
/services                Service architecture notes
/workers                 Worker architecture notes
/api                     API documentation and examples
/utils                   Utility scripts (sample audio generation)
```

## Local launch (Mac, non-technical quick path)

Use 4 terminals: **Redis**, **API**, **Worker**, **Flutter**.

### 0) One-time setup (Mac)

```bash
brew install redis ffmpeg python@3.12
```

### 1) Terminal A — start Redis

```bash
redis-server --port 6379 --save "" --appendonly no
```

### 2) Terminal B — start backend API

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
mkdir -p ../data ../models
VOCALFIT_REDIS_URL=redis://localhost:6379/0 \
VOCALFIT_STORAGE_ROOT=../data \
VOCALFIT_MODEL_ROOT=../models \
VOCALFIT_USE_GPU=false \
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 3) Terminal C — start CPU worker

```bash
cd backend
source .venv/bin/activate
VOCALFIT_REDIS_URL=redis://localhost:6379/0 \
VOCALFIT_STORAGE_ROOT=../data \
VOCALFIT_MODEL_ROOT=../models \
VOCALFIT_WORKER_CAPABILITY=cpu \
VOCALFIT_USE_GPU=false \
python3 worker_cpu.py
```

### 4) Terminal D — start Flutter app

```bash
cd frontend
flutter pub get
```

Then run exactly one of these:

- **Android emulator**
  ```bash
  flutter run --dart-define=API_BASE_URL=http://10.0.2.2:8000
  ```
- **iOS simulator**
  ```bash
  flutter run --dart-define=API_BASE_URL=http://localhost:8000
  ```
- **Physical phone on same Wi-Fi**
  1) Find your Mac LAN IP:
     ```bash
     ipconfig getifaddr en0 || ipconfig getifaddr en1
     ```
  2) Start Flutter with that IP:
     ```bash
     flutter run --dart-define=API_BASE_URL=http://<YOUR_LAN_IP>:8000
     ```

### Quick health check

```bash
curl -sS http://localhost:8000/health
redis-cli -h localhost -p 6379 ping
```

Expected:
- `/health` returns `{"status":"ok"}`
- Redis returns `PONG`

### 5) Generate sample audio

```bash
python3 utils/generate_sample_audio.py
```

Outputs are written under `data/samples/`.

## Docker deployment

```bash
docker compose up --build
```

Services:

- API: `http://localhost:8000`
- API docs: `http://localhost:8000/docs`
- Redis: `localhost:6379`
- CPU worker queue: `vocalfit:jobs:cpu`
- GPU worker queue: `vocalfit:jobs:gpu`
- Dead-letter queue: `vocalfit:jobs:dead`

## Frontend env behavior (important)

- Frontend API host is read from `--dart-define=API_BASE_URL=...`.
- `frontend/.env.example` is a reference only for run configs (Flutter does not auto-load `.env` by default).
- If `API_BASE_URL` is missing or invalid, frontend safely falls back to:
  - `http://localhost:8000`

## Demo Checklist

- [ ] **Backend health check**
  - `curl -sS http://localhost:8000/health` returns `{"status":"ok"}`
- [ ] **Upload flow**
  - Vocal file upload succeeds and returns a `job_id`
- [ ] **Process flow**
  - Job moves from queued/processing to completed
- [ ] **Result rendering**
  - Results screen shows generated variations and best-fit card
- [ ] **Playback**
  - Each variation can play audio (or shows clear per-card error)
- [ ] **Export**
  - Export opens playable/downloadable URL externally

Success criteria: end-to-end flow completes without placeholder behavior and user can hear/export at least one generated variation.

## Troubleshooting

### Emulator/device cannot connect to backend
- Android emulator must use `http://10.0.2.2:8000` (not `localhost`).
- iOS simulator uses `http://localhost:8000`.
- Physical phone must use Mac LAN IP (`http://<LAN_IP>:8000`), and both devices must be on same Wi-Fi.
- Confirm backend started with `--host 0.0.0.0`.

### Socket/network errors in app
- Verify API and worker are both running.
- Verify Redis is running and returns `PONG`.
- Recheck `API_BASE_URL` value passed to `flutter run --dart-define=...`.

### Media playback failures
- Open the variation `media_url` directly in a browser.
- If URL is relative (`/media/...`), frontend auto-resolves against `API_BASE_URL`; check that base URL is correct.
- Confirm generated files exist under `data/outputs`.

### Export URL launch failures
- Usually means empty/invalid `media_url` or device cannot open the URL scheme.
- Verify variation has a non-empty `media_url` in `/results/{job_id}` response.

### CORS issues
- Update `VOCALFIT_CORS_ORIGINS` (comma-separated list) to include your frontend origin.
- Example local values: `http://localhost:3000,http://localhost:5173,http://localhost:8000`.

### Missing env values
- Backend: copy from `backend/.env.example`.
- Frontend: always pass `API_BASE_URL` via `--dart-define`.
- Missing frontend base URL falls back to `http://localhost:8000`.

## Staging Deployment Checklist

- [ ] Backend `.env` is based on `backend/.env.example` with explicit values for:
  - `VOCALFIT_REDIS_URL`
  - `VOCALFIT_STORAGE_ROOT`
  - `VOCALFIT_MODEL_ROOT`
  - `VOCALFIT_CORS_ORIGINS` (not `*` in staging)
- [ ] Frontend build defines `API_BASE_URL` pointing to staging API
- [ ] Redis, API, and at least one worker are running and healthy
- [ ] `/health` returns OK and `/media/...` URLs are publicly reachable by app clients
- [ ] Upload -> process -> status -> results flow completes for staging sample files
- [ ] Playback works from returned media URLs
- [ ] Export opens/downloads selected media URL
- [ ] Logs capture API and worker errors with actionable messages

## Notes

- This MVP is intentionally conservative in DSP to reduce robotic artifacts.
- Demucs and neural checkpoints are pluggable; fallback paths keep the pipeline runnable in constrained environments.
- SaaS routing supports queue-based CPU/GPU dispatch, worker capability tracking, retry counts, and dead-letter handling.
- See `api/README.md` for endpoint examples and payloads.
