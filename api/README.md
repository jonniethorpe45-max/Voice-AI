# VocalFit AI API Documentation

Base URL: `http://localhost:8000`

## Endpoints

### `POST /upload`

Upload required vocal and optional song/instrumental.

**Form-data fields**
- `vocal_track` (file, required) — WAV/MP3/M4A
- `instrumental_track` (file, optional) — WAV/MP3/M4A

**Response**
```json
{
  "job_id": "uuid",
  "status": "uploaded",
  "created_at": "2026-03-28T12:00:00.000000+00:00"
}
```

### `POST /process`

Queue a transformation job.

**Body**
```json
{
  "job_id": "uuid",
  "style_controls": {
    "warmth": 0.55,
    "brightness": 0.6,
    "power": 0.7,
    "breathiness": 0.3,
    "smoothness": 0.65,
    "emotion_intensity": 0.75,
    "soft_pitch_strength": 0.4
  },
  "preferred_variations": [
    "Studio Clean",
    "Power Vocal"
  ]
}
```

**Response**
```json
{
  "job_id": "uuid",
  "status": "queued",
  "queued_at": "2026-03-28T12:00:05.000000+00:00"
}
```

### `GET /status/{job_id}`

Track job progress and errors.

**Response**
```json
{
  "job_id": "uuid",
  "status": "running",
  "progress": 45,
  "message": "Running analysis and transformation pipeline...",
  "updated_at": "2026-03-28T12:00:10.000000+00:00",
  "error": null
}
```

### `GET /results/{job_id}`

Retrieve generated vocal variations and analysis summary.

**Response**
```json
{
  "job_id": "uuid",
  "status": "completed",
  "message": "Vocal transformation complete.",
  "analysis": {
    "key": "A",
    "scale": "major"
  },
  "variations": [
    {
      "label": "Studio Clean",
      "media_url": "/media/outputs/uuid/mixed/studio_clean.wav",
      "metadata": {
        "compression_ratio": 2.2
      }
    }
  ]
}
```

## Interactive docs

- Swagger UI: `/docs`
- ReDoc: `/redoc`
