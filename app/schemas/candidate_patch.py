from dataclasses import dataclass, field

from app.domain.artifacts.enums import ArtifactFamily
from app.domain.pipeline.enums import PipelineStage
from app.schemas._base import ArtifactStub


@dataclass(frozen=True, slots=True)
class CandidatePatch(ArtifactStub):
    artifact_family: ArtifactFamily = field(
        init=False,
        default=ArtifactFamily.CANDIDATE_PATCH,
    )
    stage: PipelineStage = field(
        init=False,
        default=PipelineStage.CANDIDATE_GENERATION,
    )
    design_artifact_id: str = ""
    summary: str = "Placeholder candidate patch generated from an existing design."
