from __future__ import annotations

import librosa
import numpy as np

from .types import AnalysisResult, SectionInfo


def _extract_note_segments(f0: np.ndarray, sr: int, hop_length: int) -> list[dict]:
    notes: list[dict] = []
    active = f0 > 0
    if not active.any():
        return notes
    indices = np.where(active)[0]
    splits = np.where(np.diff(indices) > 1)[0]
    chunks = np.split(indices, splits + 1)
    for chunk in chunks:
        segment = f0[chunk]
        midi = librosa.hz_to_midi(segment[segment > 0])
        if midi.size == 0:
            continue
        notes.append(
            {
                "start_sec": round(float(chunk[0] * hop_length / sr), 3),
                "end_sec": round(float(chunk[-1] * hop_length / sr), 3),
                "mean_midi": round(float(np.mean(midi)), 2),
            }
        )
    return notes


def _detect_sections(duration_sec: float) -> list[SectionInfo]:
    if duration_sec <= 0:
        return [SectionInfo(name="verse", start_sec=0.0, end_sec=10.0, energy=0.5)]
    third = duration_sec / 3
    return [
        SectionInfo(name="verse", start_sec=0.0, end_sec=third, energy=0.46),
        SectionInfo(name="chorus", start_sec=third, end_sec=2 * third, energy=0.78),
        SectionInfo(name="bridge", start_sec=2 * third, end_sec=duration_sec, energy=0.62),
    ]


def _breath_events(y: np.ndarray, sr: int) -> list[dict]:
    rms = librosa.feature.rms(y=y, frame_length=1024, hop_length=256)[0]
    threshold = np.percentile(rms, 25)
    low = np.where(rms < threshold)[0]
    if low.size == 0:
        return []
    splits = np.where(np.diff(low) > 1)[0]
    chunks = np.split(low, splits + 1)
    events: list[dict] = []
    for chunk in chunks:
        if chunk.size < 3:
            continue
        events.append(
            {
                "start_sec": round(float(chunk[0] * 256 / sr), 3),
                "end_sec": round(float(chunk[-1] * 256 / sr), 3),
            }
        )
    return events[:48]


class AudioAnalyzer:
    def run(self, *, vocal_path, song_path) -> AnalysisResult:
        y, sr = librosa.load(vocal_path, sr=None, mono=True)
        music, _ = librosa.load(song_path, sr=sr, mono=True) if song_path else (y, sr)
        hop = 256

        f0, voiced_flag, voiced_prob = librosa.pyin(
            y,
            fmin=librosa.note_to_hz("C2"),
            fmax=librosa.note_to_hz("C7"),
            sr=sr,
            frame_length=2048,
            hop_length=hop,
        )
        f0 = np.nan_to_num(f0, nan=0.0)
        times = librosa.times_like(f0, sr=sr, hop_length=hop)
        voiced = f0[f0 > 0]
        midi = librosa.hz_to_midi(voiced) if voiced.size else np.array([60.0])
        mean_midi = float(np.mean(midi))

        key_names = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
        key = key_names[int(round(mean_midi)) % 12]
        chroma = librosa.feature.chroma_stft(y=music, sr=sr)
        chord_roots = np.argmax(chroma, axis=0)
        chords = [key_names[i] for i in chord_roots[:64]]

        tempo = int(round(float(librosa.feature.tempo(y=y, sr=sr).item())))
        notes = _extract_note_segments(f0, sr=sr, hop_length=hop)
        breaths = _breath_events(y, sr=sr)
        loudness = librosa.feature.rms(y=y, frame_length=1024, hop_length=hop)[0].tolist()
        duration = len(y) / sr if sr else 0.0
        sections = _detect_sections(duration)

        phrasing = [
            {
                "section": sec.name,
                "target_intensity": sec.energy,
                "timing_tightness": 0.87 if sec.name == "chorus" else 0.72,
            }
            for sec in sections
        ]

        return AnalysisResult(
            pitch_curve=[(round(float(t), 4), round(float(v), 3)) for t, v in zip(times[:5000], f0[:5000])],
            note_segments=notes,
            timing_map={"tempo_hint_bpm": tempo},
            phrasing=phrasing,
            breath_events=breaths,
            loudness_envelope=loudness[:2000],
            key=key,
            scale="major",
            chord_progression=chords,
            sections=sections,
            metadata={
                "mean_midi": round(mean_midi, 2),
                "voicing_ratio": round(float(np.mean(voiced_flag)) if voiced_flag is not None else 0.0, 3),
                "voiced_probability": round(
                    float(np.nanmean(voiced_prob)) if voiced_prob is not None else 0.0,
                    3,
                ),
            },
        )
