from dataclasses import dataclass, field

from app.domain.artifacts.enums import ArtifactFamily
from app.domain.pipeline.enums import PipelineStage
from app.domain.reviewability.enums import ChallengePosture, VerificationPosture
from app.schemas._base import ArtifactStub


@dataclass(frozen=True, slots=True)
class ConfidenceShapingSummary(ArtifactStub):
    """
    Non-authoritative confidence summary assembled from falsification and verification.

    downgrade_factors: reasons the proposal was downgraded (empty if PASSED).
    overall_confidence_narrative: human-readable non-authoritative summary for
      the review surface; must not use prohibited authoritative language.

    Phase 1 placeholder uses default values for all fields.
    """

    artifact_family: ArtifactFamily = field(
        init=False,
        default=ArtifactFamily.CONFIDENCE_SHAPING_SUMMARY,
    )
    stage: PipelineStage = field(
        init=False,
        default=PipelineStage.PROPOSAL_PACKAGING,
    )
    falsification_artifact_id: str = ""
    verification_artifact_id: str = ""
    challenge_posture: ChallengePosture = ChallengePosture.PASSED
    verification_posture: VerificationPosture = VerificationPosture.MIXED
    downgrade_factors: tuple[str, ...] = ("placeholder-downgrade-factor",)
    overall_confidence_narrative: str = "Placeholder confidence narrative."
    summary: str = "Non-authoritative placeholder confidence shaping summary."
