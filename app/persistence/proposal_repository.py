"""
Proposal repository persistence stub for forgeHQ — Phase 5.

Records proposal rows with explicit separation between:
- proposal_lifecycle_state  (forgeHQ workflow state — never equals operator decision)
- operator_decision_state   (human decision — never collapsed into lifecycle state)

Hard rule: these two states must never be treated as the same field.

DataForge wiring is pending Phase 5 DataForge integration.
"""
from dataclasses import dataclass

from app.domain.reviewability.enums import (
    OperatorDecisionState,
    ProposalLifecycleState,
    ReviewabilityState,
)


@dataclass(frozen=True, slots=True)
class ProposalRow:
    run_id: str
    proposal_artifact_id: str
    reviewability_state: ReviewabilityState
    # Lifecycle and decision are explicitly separate fields — never collapse.
    proposal_lifecycle_state: ProposalLifecycleState
    operator_decision_state: OperatorDecisionState


class ProposalRepository:
    """
    In-memory proposal row store.

    DataForge wiring is pending Phase 5 DataForge integration.
    """

    def __init__(self) -> None:
        self._rows: dict[str, ProposalRow] = {}  # keyed by proposal_artifact_id

    def save(self, row: ProposalRow) -> None:
        """Persist a proposal row. Overwrites if the artifact_id already exists."""
        self._rows[row.proposal_artifact_id] = row

    def get(self, proposal_artifact_id: str) -> ProposalRow | None:
        return self._rows.get(proposal_artifact_id)

    def list_by_run(self, run_id: str) -> list[ProposalRow]:
        return [r for r in self._rows.values() if r.run_id == run_id]

    def count(self) -> int:
        return len(self._rows)
