from __future__ import annotations

import time

from app.config import settings
from app.queue import (
    QueueName,
    enqueue_job,
    increment_attempt,
    move_to_dead_letter,
    pop_job,
    should_retry,
    update_job_data,
)
from workers.job_runner import process_payload


def _resolve_capability(capability_override: str | None = None) -> QueueName:
    capability = (capability_override or settings.worker_capability).lower().strip()
    return QueueName.GPU if capability == "gpu" else QueueName.CPU


def main(capability_override: str | None = None) -> None:
    settings.ensure_storage()
    queue = _resolve_capability(capability_override)
    print(f"VocalFit worker started (capability={queue.value})")

    while True:
        payload = pop_job(queue=queue)
        if payload is None:
            time.sleep(0.2)
            continue

        job_id = payload.get("job_id")
        if not job_id:
            continue

        try:
            process_payload(payload=payload, capability=queue)
        except Exception as exc:  # pragma: no cover
            reason = f"{type(exc).__name__}: {exc}"
            attempted_payload = increment_attempt(payload)

            if should_retry(attempted_payload):
                enqueue_job(attempted_payload, queue=queue)
                update_job_data(
                    job_id,
                    status="queued",
                    message=f"Retrying job ({attempted_payload['attempt']}/{settings.max_job_retries}): {reason}",
                    retry_count=int(attempted_payload["attempt"]),
                    error=reason,
                )
            else:
                move_to_dead_letter(attempted_payload, reason=reason)
                update_job_data(
                    job_id,
                    status="failed",
                    message=reason,
                    error=reason,
                    retry_count=int(attempted_payload["attempt"]),
                    dead_lettered=True,
                )


if __name__ == "__main__":
    main()
