# Workers

`backend/worker.py` is the async job worker that:

1. pulls jobs from Redis (`vocalfit:jobs`)
2. runs the VocalFit transformation pipeline
3. writes status + results back to Redis

Run locally:

```bash
cd backend
python3 worker.py
```
