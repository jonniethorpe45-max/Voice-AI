from __future__ import annotations

import json
from datetime import datetime, timezone
from enum import Enum
from typing import Any

import redis

from app.config import settings


class QueueName(str, Enum):
    CPU = "cpu"
    GPU = "gpu"
    DEAD = "dead"


def _utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def get_redis() -> redis.Redis:
    return redis.Redis.from_url(settings.redis_url, decode_responses=True)


def _status_key(job_id: str) -> str:
    return f"{settings.job_status_prefix}{job_id}"


def _queue_key(queue: QueueName) -> str:
    if queue == QueueName.CPU:
        return settings.queue_cpu_name
    if queue == QueueName.GPU:
        return settings.queue_gpu_name
    return settings.queue_dead_letter_name


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


def decide_queue(*, requires_gpu: bool) -> QueueName:
    return QueueName.GPU if requires_gpu else QueueName.CPU


def enqueue_job(payload: dict[str, Any], *, queue: QueueName) -> None:
    client = get_redis()
    client.rpush(_queue_key(queue), json.dumps(payload))


def pop_job(*, queue: QueueName, block_seconds: int | None = None) -> dict[str, Any] | None:
    client = get_redis()
    timeout = settings.queue_block_seconds if block_seconds is None else block_seconds
    entry = client.blpop(_queue_key(queue), timeout=timeout)
    if entry is None:
        return None
    _, body = entry
    return json.loads(body)


def move_to_dead_letter(payload: dict[str, Any], *, reason: str) -> None:
    message = {
        **payload,
        "failed_at": _utc_iso(),
        "dead_letter_reason": reason,
    }
    enqueue_job(message, queue=QueueName.DEAD)


def increment_attempt(payload: dict[str, Any]) -> dict[str, Any]:
    attempt = int(payload.get("attempt", 0)) + 1
    return {
        **payload,
        "attempt": attempt,
        "last_attempt_at": _utc_iso(),
    }


def should_retry(payload: dict[str, Any]) -> bool:
    return int(payload.get("attempt", 0)) < settings.max_job_retries
