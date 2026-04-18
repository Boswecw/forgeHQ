from dataclasses import dataclass, field

from app.domain.artifacts.enums import ArtifactFamily
from app.domain.pipeline.enums import PipelineStage
from app.schemas._base import ArtifactStub


@dataclass(frozen=True, slots=True)
class CandidatePatch(ArtifactStub):
    """
    Candidate patch artifact produced by CandidateGenerationService.

    design_artifact_id links back to the CandidateDesign that authorised
    this generation. modified_refs records which context items were changed;
    all entries must be a subset of the parent ContextBundle's context_item_refs
    (scope adherence is enforced at generation time).

    Phase 1 placeholder uses default values for all fields.
    """

    artifact_family: ArtifactFamily = field(
        init=False,
        default=ArtifactFamily.CANDIDATE_PATCH,
    )
    stage: PipelineStage = field(
        init=False,
        default=PipelineStage.CANDIDATE_GENERATION,
    )
    design_artifact_id: str = ""
    # Refs actually modified by the generator — must be within context bundle scope.
    modified_refs: tuple[str, ...] = ()
    scope_adherence_verified: bool = False
    summary: str = "Placeholder candidate patch generated from an existing design."
