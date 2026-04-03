from dataclasses import dataclass, field

from app.domain.artifacts.enums import ArtifactFamily
from app.domain.pipeline.enums import PipelineStage
from app.domain.reviewability.enums import ReviewabilityState
from app.schemas._base import ArtifactStub


@dataclass(frozen=True, slots=True)
class ForgeHQProposal(ArtifactStub):
    artifact_family: ArtifactFamily = field(
        init=False,
        default=ArtifactFamily.FORGEHQ_PROPOSAL,
    )
    stage: PipelineStage = field(
        init=False,
        default=PipelineStage.PROPOSAL_PACKAGING,
    )
    confidence_summary_artifact_id: str = ""
    reviewability_state: ReviewabilityState = ReviewabilityState.NOT_REVIEWABLE
    summary: str = "Placeholder non-authoritative proposal package for human review."
