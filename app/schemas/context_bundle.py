from dataclasses import dataclass, field

from app.domain.artifacts.enums import ArtifactFamily
from app.domain.pipeline.enums import PipelineStage
from app.schemas._base import ArtifactStub


@dataclass(frozen=True, slots=True)
class ContextBundle(ArtifactStub):
    """
    Bounded single-target context bundle produced by ContextBundleService.

    scope_class is always "bounded_single_target" for Phase 2.
    context_item_refs lists the refs (code, contracts, failures, history) included
    in scope; must not exceed SCOPE_MAX_ITEMS or the service fails closed.

    Phase 1 placeholder uses default values for all fields.
    """

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
    scope_class: str = "bounded_single_target"
    context_item_refs: tuple[str, ...] = ()
    summary: str = "Placeholder context bundle for one ranked target."
