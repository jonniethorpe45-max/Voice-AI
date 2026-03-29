from __future__ import annotations

from pathlib import Path

import librosa
import numpy as np
import soundfile as sf

from .types import PerformanceEncoding


class PerformanceEncoder:
    def run(self, *, vocal_path: Path, output_dir: Path) -> PerformanceEncoding:
        y, sr = librosa.load(vocal_path, sr=None, mono=True)
        y = y.astype(np.float32)

        # Conservative imperfection control while preserving expression.
        threshold = 0.01
        mask = np.abs(y) >= threshold
        cleaned = y * mask
        cleaned *= 0.98

        encoded_path = output_dir / "encoded_performance.wav"
        sf.write(encoded_path, cleaned, sr)
        return PerformanceEncoding(
            encoded_path=encoded_path,
            metadata={
                "preserve_melody": True,
                "preserve_timing": True,
                "preserve_expression": True,
                "imperfection_reduction": "conservative",
            },
        )
