"""Reconcile observer reports into independent evidence events."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable

from .models import EvidenceClaim, EvidenceEvent, ObserverReport


class EventReconciler:
    """Collapse multiple observer bundles for one source event into one event.

    Claims are processed in append order. Within one ``(event, observer)`` report,
    the last admissible claim for each predicate is authoritative. This preserves the
    frozen CG-5/CG-11 semantics for repeated same-observer deliveries while allowing
    low-confidence rows to be filtered before they can replace admissible evidence.

    Across complete observer reports for the same event, the highest-confidence report
    is the canonical event interpretation. Other complete reports remain attached for
    provenance and disagreement analysis; they are never counted as additional
    independent trials.
    """

    REQUIRED_PREDICATES = frozenset({"participant", "skill", "outcome"})

    def reconcile(
        self,
        claims: Iterable[EvidenceClaim],
        *,
        min_confidence: float = 0.0,
        source_class: str | None = "live_probe",
    ) -> tuple[EvidenceEvent, ...]:
        if not 0.0 <= min_confidence <= 1.0:
            raise ValueError("min_confidence must be between 0 and 1")

        observer_groups: dict[tuple[str, str], list[EvidenceClaim]] = defaultdict(list)
        for claim in claims:
            if claim.confidence < min_confidence:
                continue
            if source_class is not None and claim.source_class != source_class:
                continue
            observer_groups[(claim.subject, claim.observed_by)].append(claim)

        reports_by_event: dict[str, list[tuple[str, ObserverReport]]] = defaultdict(list)
        for (event_id, observer), rows in observer_groups.items():
            values: dict[str, EvidenceClaim] = {}
            for claim in rows:
                values[claim.predicate] = claim
            if not self.REQUIRED_PREDICATES.issubset(values):
                continue
            outcome = values["outcome"].object
            if outcome not in {"success", "failure"}:
                continue
            bundle = tuple(values[key] for key in sorted(self.REQUIRED_PREDICATES))
            confidence = min(claim.confidence for claim in bundle)
            observed_at = max(claim.observed_at for claim in bundle)
            scope_id = bundle[0].scope_id
            if any(claim.scope_id != scope_id for claim in bundle):
                continue
            report = ObserverReport(
                event_id=event_id,
                observer=observer,
                participant=values["participant"].object,
                skill=values["skill"].object,
                outcome=outcome,  # type: ignore[arg-type]
                confidence=confidence,
                observed_at=observed_at,
                claim_ids=tuple(sorted(claim.claim_id for claim in bundle)),
            )
            reports_by_event[event_id].append((scope_id, report))

        events: list[EvidenceEvent] = []
        for event_id, scoped_reports in reports_by_event.items():
            scope_ids = {scope_id for scope_id, _report in scoped_reports}
            if len(scope_ids) != 1:
                continue
            reports = [report for _scope, report in scoped_reports]
            reports.sort(
                key=lambda report: (report.confidence, report.observed_at, report.observer),
                reverse=True,
            )
            canonical = reports[0]
            disagreement = any(
                (
                    report.participant,
                    report.skill,
                    report.outcome,
                )
                != (
                    canonical.participant,
                    canonical.skill,
                    canonical.outcome,
                )
                for report in reports[1:]
            )
            events.append(
                EvidenceEvent(
                    event_id=event_id,
                    scope_id=next(iter(scope_ids)),
                    participant=canonical.participant,
                    skill=canonical.skill,
                    outcome=canonical.outcome,
                    confidence=canonical.confidence,
                    observed_at=canonical.observed_at,
                    reports=tuple(reports),
                    disagreement=disagreement,
                    claim_ids=tuple(
                        sorted(claim_id for report in reports for claim_id in report.claim_ids)
                    ),
                )
            )
        return tuple(sorted(events, key=lambda event: (event.observed_at, event.event_id)))
