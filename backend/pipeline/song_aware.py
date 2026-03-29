from __future__ import annotations

from .types import SectionInfo, SectionProfile


class SongAwareAdapter:
    def build_global_profile(self, sections: list[SectionInfo]) -> SectionProfile:
        if not sections:
            return SectionProfile(section="verse", gain=0.98, brightness=-0.03, compression_ratio=2.0)
        target = max(sections, key=lambda section: section.energy)
        if target.name == "chorus":
            return SectionProfile(section="chorus", gain=1.12, brightness=0.08, compression_ratio=2.8)
        if target.name == "verse":
            return SectionProfile(section="verse", gain=0.98, brightness=-0.03, compression_ratio=2.0)
        return SectionProfile(section=target.name, gain=1.03, brightness=0.02, compression_ratio=2.4)
