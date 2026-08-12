"""Compatibility tests for repeated evidence deliveries."""

from resonance_contextgraph import EventReconciler, EvidenceClaim


def _claim(
    *,
    claim_id: str,
    predicate: str,
    object_value: str,
    confidence: float,
) -> EvidenceClaim:
    return EvidenceClaim(
        claim_id=claim_id,
        scope_id="field-1",
        subject="event-1",
        predicate=predicate,
        object=object_value,
        observed_by="agent-a",
        source_id=f"source:{predicate}",
        source_class="live_probe",
        observed_at=7,
        confidence=confidence,
        direct=True,
    )


def test_last_admissible_same_observer_claim_wins() -> None:
    claims = [
        _claim(
            claim_id="participant-1",
            predicate="participant",
            object_value="agent-a",
            confidence=0.95,
        ),
        _claim(
            claim_id="skill-1",
            predicate="skill",
            object_value="water",
            confidence=0.95,
        ),
        _claim(
            claim_id="outcome-1",
            predicate="outcome",
            object_value="success",
            confidence=0.95,
        ),
        _claim(
            claim_id="participant-2",
            predicate="participant",
            object_value="agent-a",
            confidence=0.85,
        ),
        _claim(
            claim_id="skill-2",
            predicate="skill",
            object_value="water",
            confidence=0.85,
        ),
        _claim(
            claim_id="outcome-2",
            predicate="outcome",
            object_value="success",
            confidence=0.85,
        ),
    ]

    event = EventReconciler().reconcile(claims, min_confidence=0.7)[0]

    assert event.outcome == "success"
    assert event.confidence == 0.85
    assert event.reports[0].claim_ids == ("outcome-2", "participant-2", "skill-2")


def test_low_confidence_repeat_cannot_replace_admissible_report() -> None:
    claims = [
        _claim(
            claim_id="participant-1",
            predicate="participant",
            object_value="agent-a",
            confidence=0.95,
        ),
        _claim(
            claim_id="skill-1",
            predicate="skill",
            object_value="water",
            confidence=0.95,
        ),
        _claim(
            claim_id="outcome-1",
            predicate="outcome",
            object_value="success",
            confidence=0.95,
        ),
        _claim(
            claim_id="participant-2",
            predicate="participant",
            object_value="agent-a",
            confidence=0.45,
        ),
        _claim(
            claim_id="skill-2",
            predicate="skill",
            object_value="water",
            confidence=0.45,
        ),
        _claim(
            claim_id="outcome-2",
            predicate="outcome",
            object_value="failure",
            confidence=0.45,
        ),
    ]

    event = EventReconciler().reconcile(claims, min_confidence=0.7)[0]

    assert event.outcome == "success"
    assert event.confidence == 0.95
    assert event.reports[0].claim_ids == ("outcome-1", "participant-1", "skill-1")
