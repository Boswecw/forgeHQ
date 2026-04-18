"""
Falsification service for forgeHQ — Stage 6 (Critic lane).

Challenges a CandidatePatch independently of the Generator. Must remain
structurally independent from CandidateGenerationService — the critic lane
must not share state with the generator lane.

Hard rules:
- Cannot falsify a placeholder patch.
- Cannot falsify a placeholder design.
- At least one disconfirming check from the design must be evaluated.
- Proposal is downgraded if contradictions, duplicate test warnings, or
  shallow gain indicators are found.
- Every candidate receives a falsification report — even a PASSED report
  is required as the independent challenge artifact.
"""
from app.domain.reviewability.enums import ChallengePosture
from app.schemas.candidate_design import CandidateDesign
from app.schemas.candidate_patch import CandidatePatch
from app.schemas.falsification_report import FalsificationReport


class FalsificationError(ValueError):
    """Raised when falsification cannot proceed safely."""


class FalsificationService:
    """
    Independently challenges a CandidatePatch against the CandidateDesign.

    Returns a FalsificationReport with placeholder=False.
    The Critic lane must remain structurally independent from the Generator.
    """

    def challenge(
        self,
        run_id: str,
        candidate_patch: CandidatePatch,
        candidate_design: CandidateDesign,
        disconfirming_checks_evaluated: tuple[str, ...],
        contradictions: tuple[str, ...] = (),
        duplicate_test_warnings: tuple[str, ...] = (),
        shallow_gain_indicators: tuple[str, ...] = (),
    ) -> FalsificationReport:
        """
        Challenge the candidate patch and produce a falsification report.

        Raises FalsificationError if:
        - candidate_patch or candidate_design is a placeholder
        - no disconfirming checks from the design were evaluated

        Applies downgrade if any issues are found.
        """
        if candidate_patch.placeholder:
            raise FalsificationError(
                "cannot falsify a placeholder patch — "
                "run CandidateGenerationService first"
            )

        if candidate_design.placeholder:
            raise FalsificationError(
                "cannot falsify against a placeholder design — "
                "run CandidateDesignService first"
            )

        if not disconfirming_checks_evaluated:
            raise FalsificationError(
                "at least one disconfirming check must be evaluated — "
                "falsification without evaluated checks is not independent challenge"
            )

        downgrade_reasons, downgrade_applied, challenge_posture = _compute_challenge_posture(
            contradictions=contradictions,
            duplicate_test_warnings=duplicate_test_warnings,
            shallow_gain_indicators=shallow_gain_indicators,
        )

        residual_concerns = _build_residual_concerns(
            contradictions=contradictions,
            duplicate_test_warnings=duplicate_test_warnings,
            shallow_gain_indicators=shallow_gain_indicators,
        )

        return FalsificationReport(
            run_id=run_id,
            placeholder=False,
            challenged_patch_artifact_id=candidate_patch.artifact_id,
            contradictions=contradictions,
            duplicate_test_warnings=duplicate_test_warnings,
            shallow_gain_indicators=shallow_gain_indicators,
            downgrade_applied=downgrade_applied,
            downgrade_reasons=downgrade_reasons,
            disconfirming_checks_evaluated=disconfirming_checks_evaluated,
            challenge_posture=challenge_posture,
            residual_concerns=residual_concerns,
            parent_artifact_ids=(candidate_patch.artifact_id,),
            non_authoritative_notice=(
                "Non-authoritative falsification report. "
                "Does not claim deterministic upstream truth."
            ),
            summary=(
                f"Falsification: posture={challenge_posture.value}, "
                f"{len(contradictions)} contradiction(s), "
                f"{len(duplicate_test_warnings)} duplicate warning(s), "
                f"{len(shallow_gain_indicators)} shallow-gain indicator(s)."
            ),
        )


def _compute_challenge_posture(
    contradictions: tuple[str, ...],
    duplicate_test_warnings: tuple[str, ...],
    shallow_gain_indicators: tuple[str, ...],
) -> tuple[tuple[str, ...], bool, ChallengePosture]:
    """Return (downgrade_reasons, downgrade_applied, challenge_posture)."""
    reasons: list[str] = []

    if contradictions:
        reasons.append(
            f"{len(contradictions)} contradiction(s) detected between patch and design"
        )
    if duplicate_test_warnings:
        reasons.append(
            f"{len(duplicate_test_warnings)} duplicate-test warning(s) detected"
        )
    if shallow_gain_indicators:
        reasons.append(
            f"{len(shallow_gain_indicators)} shallow-gain indicator(s) detected"
        )

    if reasons:
        return tuple(reasons), True, ChallengePosture.DOWNGRADED

    return (), False, ChallengePosture.PASSED


def _build_residual_concerns(
    contradictions: tuple[str, ...],
    duplicate_test_warnings: tuple[str, ...],
    shallow_gain_indicators: tuple[str, ...],
) -> tuple[str, ...]:
    concerns: list[str] = []
    concerns.extend(f"contradiction: {c}" for c in contradictions)
    concerns.extend(f"duplicate test: {d}" for d in duplicate_test_warnings)
    concerns.extend(f"shallow gain: {s}" for s in shallow_gain_indicators)
    return tuple(concerns) if concerns else ("no residual concerns identified",)
