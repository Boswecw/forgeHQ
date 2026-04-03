from dataclasses import dataclass, field

from app.domain.artifacts.enums import ArtifactFamily
from app.domain.pipeline.enums import PipelineStage
from app.schemas._base import ArtifactStub


@dataclass(frozen=True, slots=True)
class ContextBundle(ArtifactStub):
    artifact_family: ArtifactFamily = field(
        init=False,
        default=ArtifactFamily.CONTEXT_BUNDLE,
    )
    stage: PipelineStage = field(
        init=False,
        default=PipelineStage.CONTEXT_CURATION,
    )
    target_id: str = "placeholder-target"
    scope_boundary_statement: str = "Placeholder bounded scope for a single target."
    summary: str = "Placeholder context bundle for one ranked target."
