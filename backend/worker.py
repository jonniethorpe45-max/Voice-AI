from __future__ import annotations

import time
from pathlib import Path

from app.config import settings
from app.queue import get_job_data, pop_job, set_job_data, update_job_data
from app.schemas import StyleControls
from pipeline.engine import VocalTransformationEngine
from pipeline.types import EnhancementControls


def main() -> None:
    settings.ensure_storage()
    engine = VocalTransformationEngine()
    print("VocalFit worker started")

    while True:
        payload = pop_job(block_seconds=2)
        if payload is None:
            time.sleep(0.2)
            continue

        job_id = payload.get("job_id")
        if not job_id:
            continue

        state = get_job_data(job_id)
        if not state:
            continue

        try:
            update_job_data(
                job_id,
                status="running",
                progress=20,
                message="Running analysis and transformation pipeline...",
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

            result = engine.run(
                vocal_path=vocal_path,
                song_path=song_path,
                output_dir=settings.output_dir / job_id,
                controls=enhancement,
                preferred_variations=payload.get("preferred_variations", []),
            )

            outputs = []
            for variation in result.variations:
                rel = variation.output_path.relative_to(settings.storage_root).as_posix()
                outputs.append(
                    {
                        "label": variation.label,
                        "media_url": f"/media/{rel}",
                        "metadata": variation.mix_profile,
                    }
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
                    "error": None,
                },
            )
        except Exception as exc:  # pragma: no cover
            update_job_data(
                job_id,
                status="failed",
                message=f"{type(exc).__name__}: {exc}",
                error=f"{type(exc).__name__}: {exc}",
            )


if __name__ == "__main__":
    main()
