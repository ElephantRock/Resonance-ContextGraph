"""Storage-neutral evidence types.

These types intentionally model evidence, not canonical truth and not agent belief.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

Outcome = Literal["success", "failure"]


@dataclass(frozen=True, slots=True)
class EvidenceClaim:
    """One immutable provenance-bearing assertion."""

    claim_id: str
    scope_id: str
    subject: str
    predicate: str
    object: str
    observed_by: str
    source_id: str
    source_class: str
    observed_at: int
    confidence: float = 1.0
    direct: bool = True
    valid_from: int | None = None
    valid_until: int | None = None

    def __post_init__(self) -> None:
        required = (
            self.claim_id,
            self.scope_id,
            self.subject,
            self.predicate,
            self.object,
            self.observed_by,
            self.source_id,
            self.source_class,
        )
        if not all(required):
            raise ValueError("claim identity, content, and provenance must be non-empty")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("claim confidence must be between 0 and 1")
        if self.valid_until is not None and self.valid_from is not None:
            if self.valid_until < self.valid_from:
                raise ValueError("valid_until cannot precede valid_from")

    def valid_at(self, as_of: int) -> bool:
        start = self.observed_at if self.valid_from is None else self.valid_from
        if as_of < start:
            return False
        return self.valid_until is None or as_of <= self.valid_until


@dataclass(frozen=True, slots=True)
class ObserverReport:
    """A complete observer report about one underlying event."""

    event_id: str
    observer: str
    participant: str
    skill: str
    outcome: Outcome
    confidence: float
    observed_at: int
    claim_ids: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.event_id or not self.observer or not self.participant or not self.skill:
            raise ValueError("report event, observer, participant, and skill must be non-empty")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("report confidence must be between 0 and 1")
        if not self.claim_ids:
            raise ValueError("report must preserve source claim ids")


@dataclass(frozen=True, slots=True)
class EvidenceEvent:
    """One reconciled independent event with contradiction metadata."""

    event_id: str
    scope_id: str
    participant: str
    skill: str
    outcome: Outcome
    confidence: float
    observed_at: int
    reports: tuple[ObserverReport, ...]
    disagreement: bool
    claim_ids: tuple[str, ...]

    @property
    def success(self) -> bool:
        return self.outcome == "success"

    @property
    def observer_count(self) -> int:
        return len(self.reports)


@dataclass(frozen=True, slots=True)
class MissionSpec:
    """Minimal decision query required by the context compiler."""

    mission_id: str
    lead_skill: str
    support_skill: str

    @property
    def required_skills(self) -> tuple[str, str]:
        return self.lead_skill, self.support_skill
