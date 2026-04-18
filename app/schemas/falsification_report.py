from dataclasses import dataclass, field

from app.domain.artifacts.enums import ArtifactFamily
from app.domain.pipeline.enums import PipelineStage
from app.domain.reviewability.enums import ChallengePosture
from app.schemas._base import ArtifactStub


@dataclass(frozen=True, slots=True)
class FalsificationReport(ArtifactStub):
    """
    Independent challenge artifact produced by FalsificationService.

    Structurally independent from the Generator lane — the Critic/Falsifier
    must never share state with the Generator.

    challenge_posture summarises the outcome:
      - PASSED: no issues detected
      - DOWNGRADED: issues found; proposal demoted but not blocked
      - FAILED: critical issues; proposal not reviewable without rework

    Phase 1 placeholder uses default values for all fields.
    """

    artifact_family: ArtifactFamily = field(
        init=False,
        default=ArtifactFamily.FALSIFICATION_REPORT,
    )
    stage: PipelineStage = field(
        init=False,
        default=PipelineStage.FALSIFICATION,
    )
    challenged_patch_artifact_id: str = ""
    contradictions: tuple[str, ...] = ()
    duplicate_test_warnings: tuple[str, ...] = ()
    shallow_gain_indicators: tuple[str, ...] = ()
    downgrade_applied: bool = False
    downgrade_reasons: tuple[str, ...] = ()
    disconfirming_checks_evaluated: tuple[str, ...] = ()
    challenge_posture: ChallengePosture = ChallengePosture.PASSED
    residual_concerns: tuple[str, ...] = ("placeholder-falsification-concern",)
    summary: str = "Placeholder falsification report for the candidate patch."
