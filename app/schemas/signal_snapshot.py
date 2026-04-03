from dataclasses import dataclass, field

from app.domain.artifacts.enums import ArtifactFamily
from app.domain.pipeline.enums import PipelineStage
from app.schemas._base import ArtifactStub


@dataclass(frozen=True, slots=True)
class SignalSnapshot(ArtifactStub):
    artifact_family: ArtifactFamily = field(
        init=False,
        default=ArtifactFamily.SIGNAL_SNAPSHOT,
    )
    stage: PipelineStage = field(
        init=False,
        default=PipelineStage.SIGNAL_INTAKE,
    )
    source_refs: tuple[str, ...] = ("placeholder://signal-snapshot",)
    summary: str = "Placeholder admitted signal snapshot."
