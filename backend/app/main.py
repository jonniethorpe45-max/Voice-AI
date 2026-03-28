from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.queue import enqueue_job, get_job_data, set_job_data, update_job_data
from app.schemas import (
    JobResultResponse,
    JobStatusResponse,
    ProcessRequest,
    ProcessResponse,
    UploadResponse,
    VariationResult,
)

settings.ensure_storage()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="VocalFit AI song-aware vocal transformation API",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/media", StaticFiles(directory=str(settings.storage_root)), name="media")


def _validate_audio_file(file: UploadFile) -> str:
    ext = Path(file.filename or "").suffix.lower()
    if ext not in settings.allowed_audio_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported format '{ext}'. Allowed: {sorted(settings.allowed_audio_extensions)}",
        )
    return ext


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/upload", response_model=UploadResponse)
async def upload(
    vocal_track: UploadFile = File(...),
    instrumental_track: UploadFile | None = File(default=None),
) -> UploadResponse:
    vocal_ext = _validate_audio_file(vocal_track)
    song_ext = _validate_audio_file(instrumental_track) if instrumental_track else None

    job_id = str(uuid4())
    upload_dir = settings.upload_dir / job_id
    upload_dir.mkdir(parents=True, exist_ok=True)

    vocal_path = upload_dir / f"vocal{vocal_ext}"
    vocal_data = await vocal_track.read()
    if len(vocal_data) > settings.max_upload_size_bytes:
        raise HTTPException(status_code=413, detail="Vocal file exceeds max size")
    vocal_path.write_bytes(vocal_data)

    song_path: Path | None = None
    if instrumental_track:
        song_path = upload_dir / f"song{song_ext}"
        song_data = await instrumental_track.read()
        if len(song_data) > settings.max_upload_size_bytes:
            raise HTTPException(status_code=413, detail="Song file exceeds max size")
        song_path.write_bytes(song_data)

    created_at = datetime.now(timezone.utc)
    set_job_data(
        job_id,
        {
            "job_id": job_id,
            "status": "uploaded",
            "progress": 5,
            "message": "Files uploaded successfully.",
            "created_at": created_at.isoformat(),
            "updated_at": created_at.isoformat(),
            "input": {"vocal_path": str(vocal_path), "song_path": str(song_path) if song_path else None},
            "analysis": {},
            "results": [],
            "error": None,
        },
    )
    return UploadResponse(job_id=job_id, status="uploaded", created_at=created_at)


@app.post("/process", response_model=ProcessResponse)
async def process(request: ProcessRequest) -> ProcessResponse:
    state = get_job_data(request.job_id)
    if state is None:
        raise HTTPException(status_code=404, detail="Unknown job_id")

    enqueue_job(
        {
            "job_id": request.job_id,
            "style_controls": request.style_controls.model_dump(),
            "preferred_variations": request.preferred_variations,
        }
    )
    queued_at = datetime.now(timezone.utc)
    update_job_data(
        request.job_id,
        status="queued",
        progress=max(int(state.get("progress", 0)), 10),
        message="Queued for processing.",
        queued_at=queued_at.isoformat(),
    )
    return ProcessResponse(job_id=request.job_id, status="queued", queued_at=queued_at)


@app.get("/status/{job_id}", response_model=JobStatusResponse)
async def status(job_id: str) -> JobStatusResponse:
    state = get_job_data(job_id)
    if state is None:
        raise HTTPException(status_code=404, detail="Unknown job_id")
    return JobStatusResponse(
        job_id=job_id,
        status=state["status"],
        progress=int(state.get("progress", 0)),
        message=state.get("message", ""),
        updated_at=datetime.fromisoformat(state["updated_at"]),
        error=state.get("error"),
    )


@app.get("/results/{job_id}", response_model=JobResultResponse)
async def results(job_id: str) -> JobResultResponse:
    state = get_job_data(job_id)
    if state is None:
        raise HTTPException(status_code=404, detail="Unknown job_id")
    if state["status"] not in {"completed", "completed_with_warnings"}:
        raise HTTPException(status_code=409, detail="Job not completed yet")

    variations = [
        VariationResult(
            label=item["label"],
            media_url=item["media_url"],
            metadata=item.get("metadata", {}),
        )
        for item in state.get("results", [])
    ]
    return JobResultResponse(
        job_id=job_id,
        status=state["status"],
        message=state.get("message", ""),
        analysis=state.get("analysis", {}),
        variations=variations,
    )
