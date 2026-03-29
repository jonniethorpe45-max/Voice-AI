from __future__ import annotations

from pathlib import Path
from typing import Any

from app.config import settings
from app.queue import QueueName, get_job_data, set_job_data, update_job_data
from app.schemas import StyleControls
from pipeline.engine import VocalTransformationEngine
from pipeline.types import EnhancementControls


def run_job_payload(*, payload: dict[str, Any], capability: QueueName) -> None:
    job_id = payload.get("job_id")
    if not job_id:
        return

    state = get_job_data(job_id)
    if not state:
        return

    requires_gpu = bool(payload.get("requires_gpu", False))
    if requires_gpu and capability != QueueName.GPU:
        raise RuntimeError("GPU-required job routed to non-GPU worker.")
    if not requires_gpu and capability != QueueName.CPU:
        raise RuntimeError("CPU-designated job routed to non-CPU worker.")

    update_job_data(
        job_id,
        status="running",
        progress=20,
        message=f"Processing with {capability.value.upper()} worker...",
        worker_capability=capability.value,
        error=None,
    )

    vocal_path = Path(state["input"]["vocal_path"])
    song_path_value = state["input"].get("song_path")
    song_path = Path(song_path_value) if song_path_value else None

    controls = StyleControls(**payload.get("style_controls", {}))
    enhancement = EnhancementControls(
        warmth=controls.warmth,
        brightness=controls.brightness,
        power=controls.power,
        breathiness=controls.breathiness,
        smoothness=controls.smoothness,
        emotion_intensity=controls.emotion_intensity,
        soft_pitch_strength=controls.soft_pitch_strength,
    )

    engine = VocalTransformationEngine()
    result = engine.run(
        vocal_path=vocal_path,
        song_path=song_path,
        output_dir=settings.output_dir / job_id,
        controls=enhancement,
        preferred_variations=payload.get("preferred_variations", []),
    )

    outputs: list[dict[str, Any]] = []
    for index, variation in enumerate(result.variations, start=1):
        rel = variation.output_path.relative_to(settings.storage_root).as_posix()
        metadata = {
            **variation.mix_profile,
            "song_fit_score": variation.song_fit.to_dict() if variation.song_fit else {},
        }
        outputs.append(
            {
                "label": variation.label,
                "media_url": f"/media/{rel}",
                "song_fit_score": variation.song_fit.total if variation.song_fit else 0.0,
                "rank": index,
                "metadata": metadata,
            }
        )

    selected = next(
        (item for item in outputs if item["label"] == result.selected_variation_label),
        outputs[0] if outputs else None,
    )

    set_job_data(
        job_id,
        {
            **state,
            "status": "completed",
            "progress": 100,
            "message": "Vocal transformation complete.",
            "analysis": result.analysis.to_summary(),
            "results": outputs,
            "selected_variation_label": result.selected_variation_label,
            "selected_variation": selected,
            "worker_capability": capability.value,
            "retry_count": int(payload.get("attempt", 0)),
            "error": None,
        },
    )
