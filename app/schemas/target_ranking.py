from dataclasses import dataclass, field

from app.domain.artifacts.enums import ArtifactFamily
from app.domain.pipeline.enums import PipelineStage
from app.schemas._base import ArtifactStub


@dataclass(frozen=True, slots=True)
class TargetRanking(ArtifactStub):
    artifact_family: ArtifactFamily = field(
        init=False,
        default=ArtifactFamily.TARGET_RANKING,
    )
    stage: PipelineStage = field(
        init=False,
        default=PipelineStage.TARGET_RANKING,
    )
    ranked_target_id: str = "placeholder-target"
    summary: str = "Placeholder ranking for a single bounded improvement target."
