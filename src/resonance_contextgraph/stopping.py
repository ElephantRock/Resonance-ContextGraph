"""Observable measurement-sufficiency stopping policies."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CheckpointObservation:
    """Observable state permitted to drive a stopping decision."""

    budget: int
    pair_vector: tuple[str, ...]
    minimum_selected_role_event_support: int = 0
    minimum_selected_role_score_margin: float = 0.0


@dataclass(frozen=True, slots=True)
class StopDecision:
    stop: bool
    budget: int
    reason: str


@dataclass(frozen=True, slots=True)
class PairStabilityStopper:
    """CG-11 validated stopping rule, parameterized for reuse.

    Defaults reproduce the confirmed rule: at or after 60 events, stop when the
    selected-pair vector exactly matches the immediately preceding checkpoint;
    otherwise hard-stop at 168.
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
