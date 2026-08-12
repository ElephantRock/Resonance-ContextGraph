"""Evidence-acquisition scheduling that never inspects evaluator truth."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class MeasurementCell:
    agent_id: str
    skill: str
    reconciled_event_count: int

    def __post_init__(self) -> None:
        if not self.agent_id or not self.skill:
            raise ValueError("measurement cell identity must be non-empty")
        if self.reconciled_event_count < 0:
            raise ValueError("reconciled_event_count cannot be negative")


class BalancedRoundRobin:
    """Choose the least-measured available agent/skill cell deterministically."""

    policy_name = "uniform_round_robin"

    @staticmethod
    def _tie_key(scope_id: str, cell: MeasurementCell) -> bytes:
        payload = (
            f"cg6-acquire|{scope_id}|uniform_round_robin|{cell.agent_id}|{cell.skill}"
        ).encode()
        return hashlib.sha256(payload).digest()

    def choose(self, scope_id: str, cells: tuple[MeasurementCell, ...]) -> MeasurementCell:
        if not scope_id:
            raise ValueError("scope_id must be non-empty")
        if not cells:
            raise ValueError("at least one available measurement cell is required")
        minimum = min(cell.reconciled_event_count for cell in cells)
        candidates = [cell for cell in cells if cell.reconciled_event_count == minimum]
        return min(candidates, key=lambda cell: self._tie_key(scope_id, cell))
