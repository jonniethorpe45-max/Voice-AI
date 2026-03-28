from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class EnhancementControls:
    warmth: float = 0.5
    brightness: float = 0.5
    power: float = 0.5
    breathiness: float = 0.3
    smoothness: float = 0.6
    emotion_intensity: float = 0.6
    soft_pitch_strength: float = 0.35


@dataclass
class SeparationResult:
    lead_vocal_path: Path
    backing_track_path: Path | None
    method: str


@dataclass
class SectionInfo:
    name: str
    start_sec: float
    end_sec: float
    energy: float


@dataclass
class AnalysisResult:
    pitch_curve: list[tuple[float, float]]
    note_segments: list[dict[str, Any]]
    timing_map: dict[str, Any]
    phrasing: list[dict[str, Any]]
    breath_events: list[dict[str, Any]]
    loudness_envelope: list[float]
    key: str
    scale: str
    chord_progression: list[str]
    sections: list[SectionInfo]
    metadata: dict[str, Any]

    def to_summary(self) -> dict[str, Any]:
        return {
            "key": self.key,
            "scale": self.scale,
            "chord_progression": self.chord_progression[:32],
            "timing_map": self.timing_map,
            "note_segments_preview": self.note_segments[:64],
            "phrasing": self.phrasing,
            "breath_events_preview": self.breath_events[:64],
            "sections": [
                {
                    "name": section.name,
                    "start_sec": section.start_sec,
                    "end_sec": section.end_sec,
                    "energy": section.energy,
                }
                for section in self.sections
            ],
            "metadata": self.metadata,
        }


@dataclass
class PerformanceEncoding:
    encoded_path: Path
    metadata: dict[str, Any]


@dataclass
class SectionProfile:
    section: str
    gain: float
    brightness: float
    compression_ratio: float


@dataclass
class SongFitScore:
    total: float
    musical_compatibility: float
    realism: float
    emotional_match: float
    mix_quality: float
    ranking_reason: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "total": round(self.total, 2),
            "musical_compatibility": round(self.musical_compatibility, 2),
            "realism": round(self.realism, 2),
            "emotional_match": round(self.emotional_match, 2),
            "mix_quality": round(self.mix_quality, 2),
            "ranking_reason": self.ranking_reason,
        }


@dataclass
class MixedVariation:
    label: str
    output_path: Path
    mix_profile: dict[str, Any]
    song_fit: SongFitScore | None = None


@dataclass
class PipelineResult:
    separated: SeparationResult
    analysis: AnalysisResult
    encoded: PerformanceEncoding
    transformed_vocal_path: Path
    variations: list[MixedVariation]
    best_variation: MixedVariation | None = None

    @property
    def selected_variation_label(self) -> str | None:
        return self.best_variation.label if self.best_variation else None
