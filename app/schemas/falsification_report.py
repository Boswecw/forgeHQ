from dataclasses import dataclass, field

from app.domain.artifacts.enums import ArtifactFamily
from app.domain.pipeline.enums import PipelineStage
from app.schemas._base import ArtifactStub


@dataclass(frozen=True, slots=True)
class FalsificationReport(ArtifactStub):
    artifact_family: ArtifactFamily = field(
        init=False,
        default=ArtifactFamily.FALSIFICATION_REPORT,
    )
    stage: PipelineStage = field(
        init=False,
        default=PipelineStage.FALSIFICATION,
    )
    challenged_patch_artifact_id: str = ""
    residual_concerns: tuple[str, ...] = ("placeholder-falsification-concern",)
    summary: str = "Placeholder falsification report for the candidate patch."
