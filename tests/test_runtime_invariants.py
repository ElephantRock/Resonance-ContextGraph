from __future__ import annotations

from resonance_contextgraph.compiler import ContextCompiler, ContextRequest
from resonance_contextgraph.estimator import EstimatorSpec
from resonance_contextgraph.measurement import BalancedRoundRobin, MeasurementCell
from resonance_contextgraph.models import EvidenceClaim, MissionSpec
from resonance_contextgraph.reconcile import EventReconciler
from resonance_contextgraph.stopping import CheckpointObservation, PairStabilityStopper
from resonance_contextgraph.store import EvidenceStore


def claim(
    claim_id: str,
    *,
    subject: str,
    predicate: str,
    object: str,
    observer: str = "observer-a",
    confidence: float = 0.95,
    source_class: str = "live_probe",
    observed_at: int = 1,
) -> EvidenceClaim:
    return EvidenceClaim(
        claim_id=claim_id,
        scope_id="field-1",
        subject=subject,
        predicate=predicate,
        object=object,
        observed_by=observer,
        source_id=claim_id,
        source_class=source_class,
        observed_at=observed_at,
        confidence=confidence,
    )


def event_claims(
    event_id: str,
    participant: str,
    skill: str,
    outcome: str,
    *,
    observer: str,
    confidence: float,
    observed_at: int,
) -> tuple[EvidenceClaim, ...]:
    return tuple(
        claim(
            f"{event_id}:{observer}:{predicate}",
            subject=event_id,
            predicate=predicate,
            object=value,
            observer=observer,
            confidence=confidence,
            observed_at=observed_at,
        )
        for predicate, value in (
            ("participant", participant),
            ("skill", skill),
            ("outcome", outcome),
        )
    )


def test_reconciliation_counts_one_event_and_preserves_disagreement() -> None:
    claims = (
        *event_claims(
            "event-1",
            "agent-a",
            "water",
            "success",
            observer="agent-a",
            confidence=0.95,
            observed_at=10,
        ),
        *event_claims(
            "event-1",
            "agent-a",
            "water",
            "failure",
            observer="scout-b",
            confidence=0.45,
            observed_at=10,
        ),
    )
    events = EventReconciler().reconcile(claims, min_confidence=0.0)
    assert len(events) == 1
    assert events[0].observer_count == 2
    assert events[0].outcome == "success"
    assert events[0].disagreement is True
    assert len(events[0].claim_ids) == 6


def test_store_is_evidence_only_and_append_only() -> None:
    store = EvidenceStore()
    row = claim(
        "membership-a",
        subject="agent-a",
        predicate="membership_state",
        object="active",
        source_class="membership",
    )
    store.ingest(row)
    assert store.claims() == (row,)
    assert not hasattr(store, "beliefs")
    try:
        store.ingest(row)
    except ValueError as error:
        assert "duplicate claim_id" in str(error)
    else:
        raise AssertionError("duplicate evidence must not overwrite prior evidence")


def test_compiler_spends_budget_on_complete_reconciled_events() -> None:
    store = EvidenceStore()
    store.extend(
        (
            claim(
                "membership-a",
                subject="agent-a",
                predicate="membership_state",
                object="active",
                source_class="membership",
            ),
            claim(
                "membership-b",
                subject="agent-b",
                predicate="membership_state",
                object="active",
                source_class="membership",
            ),
            *event_claims(
                "event-lead",
                "agent-a",
                "water",
                "success",
                observer="agent-a",
                confidence=0.95,
                observed_at=2,
            ),
            *event_claims(
                "event-support",
                "agent-b",
                "health",
                "success",
                observer="agent-b",
                confidence=0.95,
                observed_at=3,
            ),
        )
    )
    compiler = ContextCompiler(
        store,
        estimator=EstimatorSpec(kind="wilson_lower", min_support=1, fallback_score=0.35),
    )
    context = compiler.compile(
        ContextRequest(
            scope_id="field-1",
            mission=MissionSpec("mission-1", "water", "health"),
            as_of=10,
            claim_budget=8,
            min_confidence=0.7,
        )
    )
    assert context.claim_cost == 8
    assert len(context.membership_claims) == 2
    assert len(context.events) == 2
    assert all(len(event.reports[0].claim_ids) == 3 for event in context.events)
    assert context.provenance_complete is True
    assert context.best_pair(EstimatorSpec(min_support=1, fallback_score=0.35)) == (
        "agent-a",
        "agent-b",
    )


def test_pair_stability_stopper_reproduces_validated_rule() -> None:
    stopper = PairStabilityStopper()
    changed = (
        CheckpointObservation(48, ("a::b", "c::d")),
        CheckpointObservation(60, ("x::y", "c::d")),
    )
    assert stopper.choose(changed).stop is False

    stable = changed + (CheckpointObservation(72, ("x::y", "c::d")),)
    decision = stopper.choose(stable)
    assert decision.stop is True
    assert decision.budget == 72
    assert decision.reason == "pair_stability"

    forced = stable[:-1] + (
        CheckpointObservation(72, ("q::r", "c::d")),
        CheckpointObservation(96, ("s::t", "c::d")),
        CheckpointObservation(120, ("u::v", "c::d")),
        CheckpointObservation(144, ("w::x", "c::d")),
        CheckpointObservation(168, ("y::z", "c::d")),
    )
    forced_decision = stopper.choose(forced)
    assert forced_decision.stop is True
    assert forced_decision.budget == 168
    assert forced_decision.reason == "forced_maximum"


def test_balanced_round_robin_only_prefers_measurement_deficit() -> None:
    cells = (
        MeasurementCell("agent-a", "water", 3),
        MeasurementCell("agent-b", "water", 2),
        MeasurementCell("agent-c", "water", 2),
    )
    selected = BalancedRoundRobin().choose("field-1", cells)
    assert selected.reconciled_event_count == 2
    assert selected.agent_id in {"agent-b", "agent-c"}
