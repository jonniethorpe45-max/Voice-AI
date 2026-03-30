from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass

_MULTISPACE_RE = re.compile(r"\s+")
_PUNCT_RE = re.compile(r"[^\w\s]")


def normalize_name(name: str) -> str:
    clean = _PUNCT_RE.sub(" ", (name or "").upper())
    return _MULTISPACE_RE.sub(" ", clean).strip()


def normalize_address(address: str) -> str:
    clean = _PUNCT_RE.sub(" ", (address or "").upper())
    return _MULTISPACE_RE.sub(" ", clean).strip()


def source_hash(*parts: str) -> str:
    joined = "|".join((p or "").strip().upper() for p in parts)
    return hashlib.sha256(joined.encode("utf-8")).hexdigest()


@dataclass
class QualityFlags:
    quality_score: float
    probate_risk: bool
    duplicate_owner: bool
    duplicate_property: bool
    florida_manual_only: bool
    california_assignment_possible: bool


def quality_and_flags(
    *,
    state: str,
    county_key: str,
    mailing_address: str | None,
    assignment_confidence: float,
    duplicate_owner: bool = False,
    duplicate_property: bool = False,
) -> QualityFlags:
    has_mailing = bool(mailing_address and mailing_address.strip())
    score = 0.4 + (0.4 if has_mailing else 0.0) + min(max(assignment_confidence, 0.0), 1.0) * 0.2
    probate_risk = "ESTATE" in county_key.upper() or assignment_confidence < 0.35
    florida_manual_only = state.upper() == "FL"
    california_assignment_possible = state.upper() == "CA" and assignment_confidence >= 0.5
    return QualityFlags(
        quality_score=round(score, 3),
        probate_risk=probate_risk,
        duplicate_owner=duplicate_owner,
        duplicate_property=duplicate_property,
        florida_manual_only=florida_manual_only,
        california_assignment_possible=california_assignment_possible,
    )
