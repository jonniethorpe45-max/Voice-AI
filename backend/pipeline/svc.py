from __future__ import annotations

from pathlib import Path

import librosa
import numpy as np
import soundfile as sf

from .types import AnalysisResult, EnhancementControls, SectionProfile


class SVCEngine:
    """
    Lightweight SVC-style timbre transformation.
    Preserves timing/phrasing while applying gentle musical shaping.
    """

    def _soft_pitch_guidance(self, y: np.ndarray, analysis: AnalysisResult, strength: float) -> np.ndarray:
        if strength <= 0.0 or not analysis.pitch_curve:
            return y
        f0 = np.array([hz for _, hz in analysis.pitch_curve], dtype=np.float32)
        voiced = f0[f0 > 0]
        if voiced.size < 12:
            return y
        midi = librosa.hz_to_midi(voiced)
        nearest = np.round(midi)
        cents_shift = float(np.median((nearest - midi) * 100.0)) * np.clip(strength, 0.0, 1.0) * 0.22
        ratio = float(2 ** (cents_shift / 1200.0))
        guided = y * ratio
        peak = np.max(np.abs(guided)) + 1e-9
        return guided / peak if peak > 1.0 else guided

    def run(
        self,
        *,
        vocal_path: Path,
        output_path: Path,
        analysis: AnalysisResult,
        controls: EnhancementControls,
        section_profile: SectionProfile,
    ) -> Path:
        y, sr = librosa.load(vocal_path, sr=None, mono=True)
        y = y.astype(np.float32)

        y = self._soft_pitch_guidance(y, analysis, controls.soft_pitch_strength)

        tilt = float(np.clip((controls.brightness - controls.warmth) + section_profile.brightness, -1.0, 1.0))
        filtered = np.copy(y)
        if len(y) > 1:
            filtered[1:] = (1 - 0.05 * tilt) * y[1:] + (0.05 * tilt) * y[:-1]

        power_gain = 1.0 + (controls.power - 0.5) * 0.35
        smooth_mix = np.clip(controls.smoothness, 0.0, 1.0)
        smoothed = np.convolve(filtered, np.ones(9, dtype=np.float32) / 9.0, mode="same")
        enhanced = filtered * (1 - smooth_mix * 0.28) + smoothed * (smooth_mix * 0.28)
        enhanced *= power_gain * section_profile.gain

        breathiness = np.clip(controls.breathiness, 0.0, 1.0)
        if breathiness > 0.01:
            noise = np.random.normal(0.0, 0.0015 * breathiness, len(enhanced)).astype(np.float32)
            enhanced = enhanced + noise

        emotion_gain = 1.0 + (controls.emotion_intensity - 0.5) * 0.14
        enhanced *= emotion_gain

        peak = np.max(np.abs(enhanced)) + 1e-9
        if peak > 1.0:
            enhanced /= peak

        output_path.parent.mkdir(parents=True, exist_ok=True)
        sf.write(output_path, enhanced.astype(np.float32), sr)
        return output_path
