"""Bounded topology-aware context compilation over reconciled evidence."""

from __future__ import annotations

from dataclasses import dataclass

from .estimator import CellEvidence, EstimatorSpec, group_cell_evidence, score_cell
from .models import EvidenceClaim, EvidenceEvent, MissionSpec
from .reconcile import EventReconciler
from .store import EvidenceStore

Pair = tuple[str, str] | None
Cell = tuple[str, str]


@dataclass(frozen=True, slots=True)
class ContextRequest:
    scope_id: str
    mission: MissionSpec
    as_of: int
    claim_budget: int = 48
    min_confidence: float = 0.5

    def __post_init__(self) -> None:
        if self.claim_budget <= 0:
            raise ValueError("claim_budget must be positive")
        if not 0.0 <= self.min_confidence <= 1.0:
            raise ValueError("min_confidence must be between 0 and 1")


@dataclass(frozen=True, slots=True)
class CompiledContext:
    request: ContextRequest
    membership_claims: tuple[EvidenceClaim, ...]
    events: tuple[EvidenceEvent, ...]
    evidence: dict[Cell, CellEvidence]
    claim_cost: int

    @property
    def candidates(self) -> frozenset[str]:
        return frozenset(claim.subject for claim in self.membership_claims)

    @property
    def provenance_complete(self) -> bool:
        return (
            all(
                claim.claim_id and claim.source_id and claim.observed_by
                for claim in self.membership_claims
            )
            and all(event.claim_ids and event.reports for event in self.events)
        )

    def best_pair(self, estimator: EstimatorSpec) -> Pair:
        """Return deterministic evidence-ranked lead/support pair.

        This is a reference ranker over compiled evidence, not an environment outcome
        model. A consuming agent runtime may use a different decision policy.
        """
        if len(self.candidates) < 2:
            return None
        best: tuple[float, str, str, str] | None = None
        for lead_id in sorted(self.candidates):
            for support_id in sorted(self.candidates):
                if lead_id == support_id:
                    continue
                score = score_cell(
                    self.evidence.get((lead_id, self.request.mission.lead_skill)), estimator
                ) * score_cell(
                    self.evidence.get((support_id, self.request.mission.support_skill)), estimator
                )
                row = (score, f"{lead_id}::{support_id}", lead_id, support_id)
                if best is None or row[:2] > best[:2]:
                    best = row
        return None if best is None else (best[2], best[3])


class ContextCompiler:
    """Compile a complete-unit evidence context under a claim-equivalent budget."""

    def __init__(
        self,
        store: EvidenceStore,
        *,
        estimator: EstimatorSpec | None = None,
        reconciler: EventReconciler | None = None,
    ) -> None:
        self._store = store
        self._estimator = estimator or EstimatorSpec()
        self._reconciler = reconciler or EventReconciler()

    @staticmethod
    def _event_cost(event: EvidenceEvent) -> int:
        # Context cost tracks the canonical complete report, while all observer
        # provenance remains attached to the reconciled event metadata.
        return len(event.reports[0].claim_ids) if event.reports else 1

    def compile(self, request: ContextRequest) -> CompiledContext:
        latest_membership = self._store.latest_membership(
            scope_id=request.scope_id,
            as_of=request.as_of,
            min_confidence=request.min_confidence,
        )
        membership = tuple(latest_membership[key] for key in sorted(latest_membership))
        if len(membership) > request.claim_budget:
            raise ValueError("claim budget cannot represent the active membership set")

        all_claims = self._store.claims(
            scope_id=request.scope_id,
            as_of=request.as_of,
            min_confidence=request.min_confidence,
        )
        candidates = {claim.subject for claim in membership}
        required_skills = set(request.mission.required_skills)
        events = tuple(
            event
            for event in self._reconciler.reconcile(
                all_claims,
                min_confidence=request.min_confidence,
            )
            if event.scope_id == request.scope_id
            and event.participant in candidates
            and event.skill in required_skills
        )
        full_evidence = group_cell_evidence(events, candidates=candidates)

        ranked: dict[str, list[tuple[Cell, CellEvidence, float]]] = {}
        for role, skill in (
            ("lead", request.mission.lead_skill),
            ("support", request.mission.support_skill),
        ):
            rows = []
            for candidate in sorted(candidates):
                cell = (candidate, skill)
                evidence = full_evidence.get(cell, CellEvidence(0, ()))
                rows.append((cell, evidence, score_cell(evidence, self._estimator)))
            rows.sort(key=lambda row: (-row[2], -row[1].event_count, row[0][0]))
            ranked[role] = rows

        chosen: list[EvidenceEvent] = []
        used_event_ids: set[str] = set()
        cost = len(membership)
        role_index = {"lead": 0, "support": 0}
        support_target = max(1, self._estimator.min_support)

        while cost < request.claim_budget:
            progress = False
            for role in ("lead", "support"):
                rows = ranked[role]
                while role_index[role] < len(rows):
                    _cell, evidence, _score = rows[role_index[role]]
                    role_index[role] += 1
                    candidates_for_cell = [
                        event
                        for event in evidence.events[:support_target]
                        if event.event_id not in used_event_ids
                    ]
                    added = False
                    for event in candidates_for_cell:
                        event_cost = self._event_cost(event)
                        if cost + event_cost > request.claim_budget:
                            continue
                        chosen.append(event)
                        used_event_ids.add(event.event_id)
                        cost += event_cost
                        added = True
                    if added:
                        progress = True
                        break
            if not progress:
                break

        if cost < request.claim_budget:
            residual = sorted(
                (event for event in events if event.event_id not in used_event_ids),
                key=lambda event: (event.observed_at, event.event_id),
                reverse=True,
            )
            for event in residual:
                event_cost = self._event_cost(event)
                if cost + event_cost > request.claim_budget:
                    continue
                chosen.append(event)
                used_event_ids.add(event.event_id)
                cost += event_cost

        chosen.sort(key=lambda event: (event.observed_at, event.event_id))
        context_evidence = group_cell_evidence(chosen, candidates=candidates)
        return CompiledContext(
            request=request,
            membership_claims=membership,
            events=tuple(chosen),
            evidence=context_evidence,
            claim_cost=cost,
        )
