"""Observable measurement-sufficiency stopping policies."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass

from .compiler import CompiledContext
from .estimator import CellEvidence, EstimatorSpec, score_cell

Cell = tuple[str, str]


@dataclass(frozen=True, slots=True)
class CheckpointObservation:
    """Observable state permitted to drive a stopping decision."""

    budget: int
    pair_vector: tuple[str, ...]
    minimum_selected_role_event_support: int = 0
    minimum_selected_role_score_margin: float = 0.0


def checkpoint_observation(
    *,
    budget: int,
    contexts: Iterable[CompiledContext],
    full_evidence: Mapping[Cell, CellEvidence],
    estimator: EstimatorSpec,
) -> CheckpointObservation:
    """Build the complete CG-11 checkpoint observable from compiled evidence.

    The frozen evaluator did not stop on pair stability alone. It also computed the
    minimum independent-event support and the minimum selected-role score margin at
    each checkpoint. The confirmed candidate thresholds were support ``>= 0`` and
    margin ``>= 0.0``. The support threshold is therefore vacuous, while the margin
    threshold is not: distinct lead/support assignment can make one selected role
    score lower than another candidate's score for that role.

    This function intentionally consumes only reconciled evidence and compiled
    decision context. It has no evaluator-truth or environment-outcome input.
    """
    rows = tuple(contexts)
    pair_vector: list[str] = []
    selected_support: list[int] = []
    selected_margins: list[float] = []

    for context in rows:
        pair = context.best_pair(estimator)
        pair_vector.append("none" if pair is None else f"{pair[0]}::{pair[1]}")
        if pair is None:
            selected_support.extend([0, 0])
            selected_margins.extend([-1.0, -1.0])
            continue

        for agent_id, skill in (
            (pair[0], context.request.mission.lead_skill),
            (pair[1], context.request.mission.support_skill),
        ):
            selected_support.append(
                full_evidence.get((agent_id, skill), CellEvidence(0, ())).event_count
            )
            selected_score = score_cell(context.evidence.get((agent_id, skill)), estimator)
            competitor_scores = [
                score_cell(context.evidence.get((other, skill)), estimator)
                for other in context.candidates
                if other != agent_id
            ]
            runner_up = max(competitor_scores) if competitor_scores else 0.0
            selected_margins.append(selected_score - runner_up)

    return CheckpointObservation(
        budget=budget,
        pair_vector=tuple(pair_vector),
        minimum_selected_role_event_support=min(selected_support, default=0),
        minimum_selected_role_score_margin=min(selected_margins, default=-1.0),
    )


@dataclass(frozen=True, slots=True)
class StopDecision:
    stop: bool
    budget: int
    reason: str


@dataclass(frozen=True, slots=True)
class PairStabilityStopper:
    """CG-11 validated stopping rule, parameterized for reuse.

    Defaults reproduce the executed confirmatory rule: at or after 60 events, stop
    when the selected-pair vector exactly matches the immediately preceding checkpoint
    *and* the checkpoint's minimum selected-role score margin is non-negative;
    otherwise hard-stop at 168.

    The non-negative margin requirement was present in the frozen evaluator even
    though the preregistration prose described pair stability alone. It is retained
    here because architectural parity follows the executed confirmatory implementation.
    """

    checkpoints: tuple[int, ...] = (48, 60, 72, 96, 120, 144, 168)
    minimum_budget: int = 60
    hard_cap: int = 168
    stable_checkpoint_count: int = 2
    minimum_selected_role_event_support: int = 0
    minimum_selected_role_score_margin: float = 0.0

    def __post_init__(self) -> None:
        if tuple(sorted(self.checkpoints)) != self.checkpoints:
            raise ValueError("checkpoints must be sorted")
        if self.hard_cap not in self.checkpoints:
            raise ValueError("hard_cap must be a checkpoint")
        if self.minimum_budget not in self.checkpoints:
            raise ValueError("minimum_budget must be a checkpoint")
        if self.stable_checkpoint_count < 2:
            raise ValueError("stable_checkpoint_count must be at least 2")

    def decide(self, history: tuple[CheckpointObservation, ...]) -> StopDecision:
        if not history:
            raise ValueError("stopping history cannot be empty")
        current = history[-1]
        if current.budget not in self.checkpoints:
            raise ValueError(f"budget {current.budget} is not a configured checkpoint")
        if current.budget >= self.hard_cap:
            return StopDecision(True, current.budget, "forced_maximum")
        if current.budget < self.minimum_budget:
            return StopDecision(False, current.budget, "below_minimum")
        if len(history) < self.stable_checkpoint_count:
            return StopDecision(False, current.budget, "insufficient_history")

        recent = history[-self.stable_checkpoint_count :]
        stable = all(row.pair_vector == recent[0].pair_vector for row in recent[1:])
        if not stable:
            return StopDecision(False, current.budget, "pair_vector_changed")
        if current.minimum_selected_role_event_support < self.minimum_selected_role_event_support:
            return StopDecision(False, current.budget, "support_below_minimum")
        if current.minimum_selected_role_score_margin < self.minimum_selected_role_score_margin:
            return StopDecision(False, current.budget, "margin_below_minimum")
        return StopDecision(True, current.budget, "pair_stability")

    def choose(self, history: tuple[CheckpointObservation, ...]) -> StopDecision:
        """Return the first stopping decision in a complete checkpoint history."""
        prefix: list[CheckpointObservation] = []
        for row in history:
            prefix.append(row)
            decision = self.decide(tuple(prefix))
            if decision.stop:
                return decision
        last = history[-1]
        return StopDecision(False, last.budget, "continue")
