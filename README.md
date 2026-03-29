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

## Local development

### 1) Start Redis

Docker option:
```bash
docker run --rm -p 6379:6379 redis:7-alpine
```

Native option:
```bash
sudo apt-get update
sudo apt-get install -y redis-server
redis-server --port 6379 --save "" --appendonly no
```

### 2) Run backend API

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
mkdir -p /workspace/data /workspace/models
export VOCALFIT_REDIS_URL=redis://localhost:6379/0
export VOCALFIT_STORAGE_ROOT=/workspace/data
export VOCALFIT_MODEL_ROOT=/workspace/models
export VOCALFIT_USE_GPU=false
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 3) Run workers

```bash
cd backend
source .venv/bin/activate
export VOCALFIT_REDIS_URL=redis://localhost:6379/0
export VOCALFIT_STORAGE_ROOT=/workspace/data
export VOCALFIT_MODEL_ROOT=/workspace/models

# CPU worker pool
VOCALFIT_WORKER_CAPABILITY=cpu VOCALFIT_USE_GPU=false python3 worker_cpu.py

# GPU worker pool (run on GPU instance)
VOCALFIT_WORKER_CAPABILITY=gpu VOCALFIT_USE_GPU=true python3 worker_gpu.py
```

### Deterministic startup checks

After starting services, verify:

```bash
curl -sS http://localhost:8000/health
redis-cli -h localhost -p 6379 ping
```

Expected:
- `/health` returns `{"status":"ok"}`
- Redis returns `PONG`

### 4) Generate sample audio

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

## Frontend run (Flutter)

```bash
cd frontend
flutter pub get
flutter run -d chrome
```

Set API URL with:

```bash
flutter run -d chrome --dart-define=API_BASE_URL=http://localhost:8000
```

## Notes

- This MVP is intentionally conservative in DSP to reduce robotic artifacts.
- Demucs and neural checkpoints are pluggable; fallback paths keep the pipeline runnable in constrained environments.
- SaaS routing supports queue-based CPU/GPU dispatch, worker capability tracking, retry counts, and dead-letter handling.
- See `api/README.md` for endpoint examples and payloads.
