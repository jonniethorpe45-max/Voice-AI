from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from .types import SeparationResult


class SourceSeparator:
    """Demucs-first source separation with deterministic fallback."""

    def run(self, *, vocal_path: Path, song_path: Path | None, output_dir: Path) -> SeparationResult:
        output_dir.mkdir(parents=True, exist_ok=True)
        lead_vocal = output_dir / "lead_vocal.wav"
        backing = output_dir / "background_music.wav"

        if song_path is None:
            shutil.copy2(vocal_path, lead_vocal)
            shutil.copy2(vocal_path, backing)
            return SeparationResult(lead_vocal_path=lead_vocal, backing_track_path=backing, method="vocal_only")

        demucs = shutil.which("demucs")
        if demucs:
            try:
                cmd = [
                    demucs,
                    "--two-stems",
                    "vocals",
                    "--out",
                    str(output_dir),
                    str(song_path),
                ]
                subprocess.run(cmd, check=True, capture_output=True, text=True)
                demucs_root = output_dir / "htdemucs" / song_path.stem
                demucs_vocals = demucs_root / "vocals.wav"
                demucs_no_vocals = demucs_root / "no_vocals.wav"
                if demucs_vocals.exists() and demucs_no_vocals.exists():
                    shutil.copy2(demucs_vocals, lead_vocal)
                    shutil.copy2(demucs_no_vocals, backing)
                    return SeparationResult(
                        lead_vocal_path=lead_vocal,
                        backing_track_path=backing,
                        method="demucs",
                    )
            except (subprocess.CalledProcessError, FileNotFoundError):
                pass

        shutil.copy2(vocal_path, lead_vocal)
        shutil.copy2(song_path, backing)
        return SeparationResult(lead_vocal_path=lead_vocal, backing_track_path=backing, method="fallback_copy")
