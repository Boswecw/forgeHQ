from dataclasses import dataclass, field

from app.domain.artifacts.enums import ArtifactFamily
from app.domain.pipeline.enums import PipelineStage
from app.domain.reviewability.enums import (
    NotReviewableReason,
    OperatorDecisionState,
    ProposalLifecycleState,
    ReviewabilityState,
)
from app.schemas._base import ArtifactStub


@dataclass(frozen=True, slots=True)
class ForgeHQProposal(ArtifactStub):
    """
    Final human-review package assembled from the required backbone artifacts.

    reviewability_state is computed from backbone completeness — not from
    operator decision. proposal_lifecycle_state records where the proposal is
    in its own workflow; operator_decision_state records what the human decided.
    These two must never be collapsed.

    backbone_artifact_ids lists all artifact IDs that form the backbone.
    not_reviewable_reasons records why the proposal is not_reviewable, if applicable.

    Phase 1 placeholder uses default values for all fields.
    """

    artifact_family: ArtifactFamily = field(
        init=False,
        default=ArtifactFamily.FORGEHQ_PROPOSAL,
    )
    stage: PipelineStage = field(
        init=False,
        default=PipelineStage.PROPOSAL_PACKAGING,
    )
    confidence_summary_artifact_id: str = ""
    backbone_artifact_ids: tuple[str, ...] = ()
    reviewability_state: ReviewabilityState = ReviewabilityState.NOT_REVIEWABLE
    not_reviewable_reasons: tuple[NotReviewableReason, ...] = ()
    proposal_lifecycle_state: ProposalLifecycleState = ProposalLifecycleState.DRAFT
    # Operator decision state is always separate from lifecycle state.
    operator_decision_state: OperatorDecisionState = OperatorDecisionState.NO_DECISION
    summary: str = "Placeholder non-authoritative proposal package for human review."
