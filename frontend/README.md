# VocalFit AI Frontend

Premium mobile-first Flutter UI wired to the VocalFit backend API.

## Run

```bash
flutter pub get
flutter run --dart-define=API_BASE_URL=http://localhost:8000
```

For Android emulator use:

```bash
flutter run --dart-define=API_BASE_URL=http://10.0.2.2:8000
```

For iOS simulator use:

```bash
flutter run --dart-define=API_BASE_URL=http://localhost:8000
```

If `API_BASE_URL` is omitted, the app defaults to:

`http://localhost:8000`

## Production wiring included

- Real upload flow (`POST /upload`)
- Real processing trigger (`POST /process`)
- Real status polling (`GET /status/{job_id}`)
- Real results loading (`GET /results/{job_id}`)

## Playback + export

- Variation cards now support real media playback via `just_audio` when `media_url` is available.
- Export action now opens the selected variation `media_url` using `url_launcher` (external app/browser).

## UX behavior

- Home -> Upload -> Processing -> Results -> Fine Tune -> Export
- Upload screen uses device file picker for:
  - Vocal (required)
  - Song/instrumental (optional)
- Processing screen displays:
  - Server progress
  - Server message
  - Auto-refresh every 2s until completion/failure
- Results screen displays backend-generated variations and best-fit badge.

