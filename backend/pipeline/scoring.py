from __future__ import annotations

import librosa
import numpy as np

from .types import AnalysisResult, MixedVariation, SongFitScore


class SongFitScorer:
    """Rank generated variations by overall song fit."""

    @staticmethod
    def _clamp(value: float, low: float = 0.0, high: float = 100.0) -> float:
        return float(np.clip(value, low, high))

    def _musical_compatibility(self, y: np.ndarray, sr: int, analysis: AnalysisResult) -> float:
        f0, _, _ = librosa.pyin(
            y,
            fmin=librosa.note_to_hz("C2"),
            fmax=librosa.note_to_hz("C7"),
            sr=sr,
            frame_length=2048,
            hop_length=256,
        )
        f0 = np.nan_to_num(f0, nan=0.0)
        voiced = f0[f0 > 0]
        if voiced.size < 10:
            return 45.0

        key_names = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
        key_index = key_names.index(analysis.key) if analysis.key in key_names else 0
        midi_mod = np.mod(np.round(librosa.hz_to_midi(voiced)), 12)

        key_ratio = float(np.mean(midi_mod == key_index))
        chord_notes = {key_names.index(ch) for ch in analysis.chord_progression if ch in key_names}
        chord_ratio = float(np.mean(np.isin(midi_mod, list(chord_notes)))) if chord_notes else key_ratio
        return self._clamp((0.65 * key_ratio + 0.35 * chord_ratio) * 100.0)

    def _realism(self, y: np.ndarray, sr: int) -> float:
        rms = librosa.feature.rms(y=y, frame_length=1024, hop_length=256)[0]
        crest = float(np.max(np.abs(y)) / (np.mean(np.abs(y)) + 1e-8))
        rms_var = float(np.std(rms))
        crest_score = self._clamp((crest - 2.0) / 6.0 * 100.0)
        dynamics_score = self._clamp((rms_var / 0.12) * 100.0)
        clip_penalty = 12.0 if float(np.max(np.abs(y))) > 0.995 else 0.0
        return self._clamp(0.55 * crest_score + 0.45 * dynamics_score - clip_penalty)

    def _emotional_match(self, y: np.ndarray, analysis: AnalysisResult) -> float:
        rms = librosa.feature.rms(y=y, frame_length=1024, hop_length=256)[0]
        target = np.array(analysis.loudness_envelope[: len(rms)], dtype=np.float32)
        if target.size < 8:
            return 55.0
        if target.size != rms.size:
            target = np.interp(
                np.linspace(0, target.size - 1, rms.size),
                np.arange(target.size),
                target,
            )
        corr = np.corrcoef(rms, target)[0, 1] if np.std(rms) > 0 and np.std(target) > 0 else 0.0
        corr = 0.0 if np.isnan(corr) else float(corr)
        return self._clamp((corr + 1.0) * 50.0)

    def _mix_quality(self, y: np.ndarray, sr: int) -> float:
        centroid = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
        bandwidth = librosa.feature.spectral_bandwidth(y=y, sr=sr)[0]
        rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)[0]
        centroid_score = self._clamp(100.0 - abs(float(np.mean(centroid)) - 2600.0) / 2600.0 * 100.0)
        bandwidth_score = self._clamp(100.0 - abs(float(np.mean(bandwidth)) - 2200.0) / 2200.0 * 100.0)
        rolloff_score = self._clamp(100.0 - abs(float(np.mean(rolloff)) - 5400.0) / 5400.0 * 100.0)
        return self._clamp(0.35 * centroid_score + 0.30 * bandwidth_score + 0.35 * rolloff_score)

    def rank(
        self,
        *,
        variations: list[MixedVariation],
        analysis: AnalysisResult,
    ) -> tuple[list[MixedVariation], MixedVariation | None]:
        scored: list[MixedVariation] = []
        for variation in variations:
            y, sr = librosa.load(variation.output_path, sr=None, mono=True)
            musical = self._musical_compatibility(y, sr, analysis)
            realism = self._realism(y, sr)
            emotional = self._emotional_match(y, analysis)
            mix_quality = self._mix_quality(y, sr)
            total = self._clamp(
                0.35 * musical + 0.30 * realism + 0.20 * emotional + 0.15 * mix_quality
            )
            variation.song_fit = SongFitScore(
                total=round(total, 2),
                musical_compatibility=round(musical, 2),
                realism=round(realism, 2),
                emotional_match=round(emotional, 2),
                mix_quality=round(mix_quality, 2),
                ranking_reason=(
                    "Best aggregate compatibility, naturalness, emotional contour, and mix balance."
                ),
            )
            scored.append(variation)

        scored.sort(key=lambda item: item.song_fit.total if item.song_fit else 0.0, reverse=True)
        best = scored[0] if scored else None
        return scored, best
