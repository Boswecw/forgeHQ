from dataclasses import dataclass, field

from app.domain.artifacts.enums import ArtifactFamily
from app.domain.pipeline.enums import PipelineStage
from app.schemas._base import ArtifactStub


@dataclass(frozen=True, slots=True)
class CandidateVerification(ArtifactStub):
    artifact_family: ArtifactFamily = field(
        init=False,
        default=ArtifactFamily.CANDIDATE_VERIFICATION,
    )
    stage: PipelineStage = field(
        init=False,
        default=PipelineStage.VERIFICATION,
    )
    verified_patch_artifact_id: str = ""
    observed_gains: tuple[str, ...] = ("placeholder-observed-gain",)
    residual_weaknesses: tuple[str, ...] = ("placeholder-residual-weakness",)
    summary: str = "Placeholder candidate verification with explicit remaining weakness."
