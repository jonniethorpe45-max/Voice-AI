from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

import redis

from app.config import settings


def _utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def get_redis() -> redis.Redis:
    return redis.Redis.from_url(settings.redis_url, decode_responses=True)


def _status_key(job_id: str) -> str:
    return f"{settings.job_status_prefix}{job_id}"


def set_job_data(job_id: str, payload: dict[str, Any]) -> None:
    client = get_redis()
    client.set(_status_key(job_id), json.dumps(payload))
    client.expire(_status_key(job_id), settings.job_ttl_seconds)


def get_job_data(job_id: str) -> dict[str, Any] | None:
    client = get_redis()
    raw = client.get(_status_key(job_id))
    if raw is None:
        return None
    return json.loads(raw)


def update_job_data(job_id: str, **updates: Any) -> dict[str, Any] | None:
    current = get_job_data(job_id)
    if current is None:
        return None
    current.update(updates)
    current["updated_at"] = _utc_iso()
    set_job_data(job_id, current)
    return current


def enqueue_job(payload: dict[str, Any]) -> None:
    client = get_redis()
    client.rpush(settings.queue_name, json.dumps(payload))


def pop_job(block_seconds: int = 2) -> dict[str, Any] | None:
    client = get_redis()
    entry = client.blpop(settings.queue_name, timeout=block_seconds)
    if entry is None:
        return None
    _, body = entry
    return json.loads(body)
