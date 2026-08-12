"""Estimate decision-relevant capability from independent reconciled events."""

from __future__ import annotations

import math
from collections import defaultdict
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Literal

from .models import EvidenceEvent

EstimatorKind = Literal["posterior_mean", "wilson_lower"]
Cell = tuple[str, str]


@dataclass(frozen=True, slots=True)
class EstimatorSpec:
    kind: EstimatorKind = "posterior_mean"
    min_support: int = 1
    fallback_score: float = 0.5
    alpha: float = 1.0
    beta: float = 1.0
    z: float = 1.2815515655446004

    def __post_init__(self) -> None:
        if self.min_support < 0:
            raise ValueError("min_support cannot be negative")
        if not 0.0 <= self.fallback_score <= 1.0:
            raise ValueError("fallback_score must be between 0 and 1")
        if self.alpha <= 0.0 or self.beta <= 0.0:
            raise ValueError("beta prior parameters must be positive")
        if self.z < 0.0:
            raise ValueError("z cannot be negative")


@dataclass(frozen=True, slots=True)
class CellEvidence:
    successes: int
    events: tuple[EvidenceEvent, ...]

    @property
    def event_count(self) -> int:
        return len(self.events)

    @property
    def failures(self) -> int:
        return self.event_count - self.successes


def group_cell_evidence(
    events: Iterable[EvidenceEvent],
    *,
    candidates: set[str] | frozenset[str] | None = None,
) -> dict[Cell, CellEvidence]:
    grouped: dict[Cell, list[EvidenceEvent]] = defaultdict(list)
    for event in events:
        if candidates is not None and event.participant not in candidates:
            continue
        grouped[(event.participant, event.skill)].append(event)
    return {
        cell: CellEvidence(
            successes=sum(event.success for event in rows),
            events=tuple(sorted(rows, key=lambda event: (event.observed_at, event.event_id))),
        )
        for cell, rows in grouped.items()
    }


def score_cell(evidence: CellEvidence | None, spec: EstimatorSpec) -> float:
    if evidence is None or evidence.event_count < spec.min_support:
        return spec.fallback_score

    successes = evidence.successes
    total = evidence.event_count
    if spec.kind == "posterior_mean":
        return (spec.alpha + successes) / (spec.alpha + spec.beta + total)

    if spec.kind == "wilson_lower":
        phat = successes / total
        z2 = spec.z * spec.z
        denominator = 1.0 + z2 / total
        center = phat + z2 / (2.0 * total)
        radius = spec.z * math.sqrt(
            phat * (1.0 - phat) / total + z2 / (4.0 * total * total)
        )
        return max(0.0, (center - radius) / denominator)

    raise ValueError(f"unsupported estimator kind: {spec.kind}")
