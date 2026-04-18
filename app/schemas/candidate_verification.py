from dataclasses import dataclass, field

from app.domain.artifacts.enums import ArtifactFamily
from app.domain.pipeline.enums import PipelineStage
from app.domain.reviewability.enums import VerificationPosture
from app.schemas._base import ArtifactStub


@dataclass(frozen=True, slots=True)
class CandidateVerification(ArtifactStub):
    """
    Verification artifact produced by CandidateVerificationService.

    Both observed_gains and residual_weaknesses must be non-empty —
    no green-only posture is permitted. verification_posture is computed
    from the balance between gains and weaknesses:
      WEAK   — weaknesses exceed gains
      MIXED  — equal counts
      STRONG — gains exceed weaknesses

    measurement_basis records what was actually measured (branch coverage,
    mutation score, etc.). Must be non-empty or verification fails closed.

    Phase 1 placeholder uses default values for all fields.
    """

    artifact_family: ArtifactFamily = field(
        init=False,
        default=ArtifactFamily.CANDIDATE_VERIFICATION,
    )
    stage: PipelineStage = field(
        init=False,
        default=PipelineStage.VERIFICATION,
    )
    verified_patch_artifact_id: str = ""
    measurement_basis: tuple[str, ...] = ()
    observed_gains: tuple[str, ...] = ("placeholder-observed-gain",)
    residual_weaknesses: tuple[str, ...] = ("placeholder-residual-weakness",)
    verification_posture: VerificationPosture = VerificationPosture.MIXED
    summary: str = "Placeholder candidate verification with explicit remaining weakness."
