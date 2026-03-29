from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import soundfile as sf


def synth_tone(freq: float, dur: float, sr: int, amp: float = 0.2) -> np.ndarray:
    t = np.linspace(0.0, dur, int(sr * dur), endpoint=False)
    return amp * np.sin(2.0 * math.pi * freq * t)


def main() -> None:
    out_dir = Path("data/samples")
    out_dir.mkdir(parents=True, exist_ok=True)
    sr = 44100

    phrase = [
        synth_tone(261.63, 0.4, sr),  # C4
        synth_tone(293.66, 0.4, sr),  # D4
        synth_tone(329.63, 0.4, sr),  # E4
        synth_tone(392.00, 0.6, sr),  # G4
        np.zeros(int(sr * 0.2)),
        synth_tone(349.23, 0.4, sr),  # F4
        synth_tone(329.63, 0.4, sr),  # E4
        synth_tone(293.66, 0.4, sr),  # D4
        synth_tone(261.63, 0.6, sr),  # C4
    ]
    vocal = np.concatenate(phrase).astype(np.float32)

    beat = np.sin(2 * math.pi * 2.0 * np.linspace(0, len(vocal) / sr, len(vocal), endpoint=False))
    pad = synth_tone(130.81, len(vocal) / sr, sr, amp=0.06)  # C3
    instrumental = (0.08 * beat + pad).astype(np.float32)

    sf.write(out_dir / "sample_vocal.wav", vocal, sr)
    sf.write(out_dir / "sample_song.wav", instrumental, sr)
    print(f"Generated samples in {out_dir.resolve()}")


if __name__ == "__main__":
    main()
