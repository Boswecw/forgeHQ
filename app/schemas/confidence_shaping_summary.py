from dataclasses import dataclass, field

from app.domain.artifacts.enums import ArtifactFamily
from app.domain.pipeline.enums import PipelineStage
from app.schemas._base import ArtifactStub


@dataclass(frozen=True, slots=True)
class ConfidenceShapingSummary(ArtifactStub):
    artifact_family: ArtifactFamily = field(
        init=False,
        default=ArtifactFamily.CONFIDENCE_SHAPING_SUMMARY,
    )
    stage: PipelineStage = field(
        init=False,
        default=PipelineStage.PROPOSAL_PACKAGING,
    )
    falsification_artifact_id: str = ""
    verification_artifact_id: str = ""
    downgrade_factors: tuple[str, ...] = ("placeholder-downgrade-factor",)
    summary: str = "Non-authoritative placeholder confidence shaping summary."
