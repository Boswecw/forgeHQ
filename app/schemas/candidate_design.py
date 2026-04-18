from dataclasses import dataclass, field

from app.domain.artifacts.enums import ArtifactFamily
from app.domain.pipeline.enums import PipelineStage
from app.schemas._base import ArtifactStub


@dataclass(frozen=True, slots=True)
class CandidateDesign(ArtifactStub):
    """
    Candidate design artifact produced by CandidateDesignService.

    All six design fields must be non-empty before generation is permitted.
    scope_boundary_statement and target_id are copied from the parent
    ContextBundle and locked — the generator must not exceed this scope.

    Phase 1 placeholder uses default values for all fields.
    """

    artifact_family: ArtifactFamily = field(
        init=False,
        default=ArtifactFamily.CANDIDATE_DESIGN,
    )
    stage: PipelineStage = field(
        init=False,
        default=PipelineStage.CANDIDATE_DESIGN,
    )
    target_id: str = "placeholder-target"
    # Locked from parent ContextBundle — generator must stay within this boundary.
    scope_boundary_statement: str = "placeholder-scope"
    context_bundle_artifact_id: str | None = None
    change_hypothesis: str = "placeholder-change-hypothesis"
    intended_confidence_gain: str = "placeholder-confidence-gain"
    targeted_behaviors: tuple[str, ...] = ()
    oracle_strategy: str = "placeholder-oracle-strategy"
    disconfirming_checks: tuple[str, ...] = ()
    failure_hypotheses: tuple[str, ...] = ()
    summary: str = "Placeholder candidate design that exists before generation."
