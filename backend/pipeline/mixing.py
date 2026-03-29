from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path

from .types import MixedVariation


def _safe_name(label: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", label.lower()).strip("_")


class MixingEngine:
    PRESETS: dict[str, dict[str, float]] = {
        "Studio Clean": {"vocal_gain": 1.12, "music_gain": 0.9, "reverb": 0.08, "stereo": 1.0, "compress": 2.2},
        "Radio Pop": {"vocal_gain": 1.23, "music_gain": 0.86, "reverb": 0.14, "stereo": 1.1, "compress": 2.8},
        "Emotional / Soulful": {"vocal_gain": 1.17, "music_gain": 0.88, "reverb": 0.19, "stereo": 1.05, "compress": 2.0},
        "Power Vocal": {"vocal_gain": 1.3, "music_gain": 0.84, "reverb": 0.12, "stereo": 1.14, "compress": 3.2},
        "Natural Minimal Fix": {"vocal_gain": 1.07, "music_gain": 0.92, "reverb": 0.05, "stereo": 1.0, "compress": 1.8},
    }

    def __init__(self) -> None:
        self._ffmpeg = shutil.which("ffmpeg")

    def run(
        self,
        *,
        transformed_vocal: Path,
        backing_track: Path | None,
        output_dir: Path,
        preferred_variations: list[str] | None,
    ) -> list[MixedVariation]:
        selected = preferred_variations or list(self.PRESETS.keys())
        out: list[MixedVariation] = []
        for label in selected:
            profile = self.PRESETS.get(label)
            if profile is None:
                continue
            output_path = output_dir / f"{_safe_name(label)}.wav"
            self._mix(src_vocal=transformed_vocal, backing=backing_track, out_path=output_path, profile=profile)
            out.append(
                MixedVariation(
                    label=label,
                    output_path=output_path,
                    mix_profile={
                        "eq": "gentle presence + low cut",
                        "compression_ratio": profile["compress"],
                        "de_essing": "moderate",
                        "reverb_mix": profile["reverb"],
                        "stereo_width": profile["stereo"],
                    },
                )
            )
        return out

    def _mix(self, *, src_vocal: Path, backing: Path | None, out_path: Path, profile: dict[str, float]) -> None:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        if not self._ffmpeg:
            shutil.copy2(src_vocal, out_path)
            return

        if backing and backing.exists():
            filter_complex = (
                f"[0:a]highpass=f=85,lowpass=f=13000,"
                f"acompressor=threshold=-18dB:ratio={profile['compress']},"
                "deesser=i=0.4:m=0.5:f=0.5,"
                f"aecho=0.8:0.7:35:{profile['reverb']},"
                f"volume={profile['vocal_gain']}[voc];"
                f"[1:a]volume={profile['music_gain']},"
                f"stereotools=mlev={profile['stereo']}:slev={profile['stereo']}[bg];"
                "[voc][bg]amix=inputs=2:duration=longest:normalize=0[out]"
            )
            cmd = [
                self._ffmpeg,
                "-y",
                "-i",
                str(src_vocal),
                "-i",
                str(backing),
                "-filter_complex",
                filter_complex,
                "-map",
                "[out]",
                str(out_path),
            ]
        else:
            filter_chain = (
                "highpass=f=85,lowpass=f=13000,"
                f"acompressor=threshold=-18dB:ratio={profile['compress']},"
                "deesser=i=0.4:m=0.5:f=0.5,"
                f"aecho=0.8:0.7:35:{profile['reverb']},"
                f"volume={profile['vocal_gain']}"
            )
            cmd = [
                self._ffmpeg,
                "-y",
                "-i",
                str(src_vocal),
                "-af",
                filter_chain,
                str(out_path),
            ]
        try:
            subprocess.run(cmd, check=True, capture_output=True)
        except subprocess.CalledProcessError:
            shutil.copy2(src_vocal, out_path)
