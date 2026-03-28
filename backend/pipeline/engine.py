from __future__ import annotations

from pathlib import Path

from .analysis import AudioAnalyzer
from .mixing import MixingEngine
from .performance import PerformanceEncoder
from .separation import SourceSeparator
from .song_aware import SongAwareAdapter
from .svc import SVCEngine
from .types import EnhancementControls, PipelineResult


class VocalTransformationEngine:
    def __init__(self) -> None:
        self.separator = SourceSeparator()
        self.analyzer = AudioAnalyzer()
        self.performance = PerformanceEncoder()
        self.song_aware = SongAwareAdapter()
        self.svc = SVCEngine()
        self.mixer = MixingEngine()

    def run(
        self,
        *,
        vocal_path: Path,
        song_path: Path | None,
        output_dir: Path,
        controls: EnhancementControls,
        preferred_variations: list[str] | None = None,
    ) -> PipelineResult:
        output_dir.mkdir(parents=True, exist_ok=True)

        separated = self.separator.run(vocal_path=vocal_path, song_path=song_path, output_dir=output_dir)
        analysis = self.analyzer.run(vocal_path=separated.lead_vocal_path, song_path=separated.backing_track_path)
        encoded = self.performance.run(vocal_path=separated.lead_vocal_path, output_dir=output_dir)
        section_profile = self.song_aware.build_global_profile(analysis.sections)

        transformed_path = self.svc.run(
            vocal_path=encoded.encoded_path,
            output_path=output_dir / "transformed_vocal.wav",
            analysis=analysis,
            controls=controls,
            section_profile=section_profile,
        )
        variations = self.mixer.run(
            transformed_vocal=transformed_path,
            backing_track=separated.backing_track_path,
            output_dir=output_dir / "mixed",
            preferred_variations=preferred_variations,
        )
        return PipelineResult(
            separated=separated,
            analysis=analysis,
            encoded=encoded,
            transformed_vocal_path=transformed_path,
            variations=variations,
        )
