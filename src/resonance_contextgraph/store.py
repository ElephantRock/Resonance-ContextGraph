"""Append-only evidence storage.

The store deliberately has no agent-belief mutation API. Retrieval returns evidence
objects only; adoption into belief is a responsibility of a consuming agent runtime.
"""

from __future__ import annotations

from collections.abc import Iterable

from .models import EvidenceClaim


class EvidenceStore:
    """Deterministic append-only in-memory evidence store."""

    def __init__(self) -> None:
        self._claims: list[EvidenceClaim] = []
        self._claim_ids: set[str] = set()
        self._ingest_count_history: list[int] = []

    def ingest(self, claim: EvidenceClaim) -> None:
        if claim.claim_id in self._claim_ids:
            raise ValueError(f"duplicate claim_id: {claim.claim_id}")
        self._claims.append(claim)
        self._claim_ids.add(claim.claim_id)
        self._ingest_count_history.append(len(self._claims))

    def extend(self, claims: Iterable[EvidenceClaim]) -> None:
        for claim in claims:
            self.ingest(claim)

    @property
    def size(self) -> int:
        return len(self._claims)

    @property
    def ingest_count_history(self) -> tuple[int, ...]:
        return tuple(self._ingest_count_history)

    def claims(
        self,
        *,
        scope_id: str | None = None,
        as_of: int | None = None,
        min_confidence: float = 0.0,
        source_class: str | None = None,
    ) -> tuple[EvidenceClaim, ...]:
        if not 0.0 <= min_confidence <= 1.0:
            raise ValueError("min_confidence must be between 0 and 1")
        rows = []
        for claim in self._claims:
            if scope_id is not None and claim.scope_id != scope_id:
                continue
            if claim.confidence < min_confidence:
                continue
            if source_class is not None and claim.source_class != source_class:
                continue
            if as_of is not None and not claim.valid_at(as_of):
                continue
            rows.append(claim)
        return tuple(rows)

    def latest_membership(
        self,
        *,
        scope_id: str,
        as_of: int,
        min_confidence: float,
        active_value: str = "active",
    ) -> dict[str, EvidenceClaim]:
        """Return latest admissible membership claim by subject."""
        latest: dict[str, EvidenceClaim] = {}
        for claim in self.claims(
            scope_id=scope_id,
            as_of=as_of,
            min_confidence=min_confidence,
        ):
            if claim.predicate != "membership_state":
                continue
            prior = latest.get(claim.subject)
            if prior is None or (claim.observed_at, claim.claim_id) > (
                prior.observed_at,
                prior.claim_id,
            ):
                latest[claim.subject] = claim
        return {
            subject: claim
            for subject, claim in latest.items()
            if claim.object == active_value
        }
