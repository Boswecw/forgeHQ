"""
Candidate verification service for forgeHQ — Stage 7.

Records observed gains and residual weaknesses after patch evaluation.
No green-only posture is permitted — both gains and weaknesses must be present.
Missing measurement basis fails closed.

Hard rules:
- Cannot verify a placeholder patch.
- measurement_basis must be non-empty (what was actually measured).
- observed_gains must be non-empty.
- residual_weaknesses must be non-empty — no green-only posture.
- verification_posture is computed from the balance of gains vs weaknesses.
"""
from app.domain.reviewability.enums import VerificationPosture
from app.schemas.candidate_patch import CandidatePatch
from app.schemas.candidate_verification import CandidateVerification


class VerificationError(ValueError):
    """Raised when verification cannot proceed safely."""


class CandidateVerificationService:
    """
    Records gains and limitations from patch evaluation.

    Returns a CandidateVerification with placeholder=False.
    Requires both observed_gains and residual_weaknesses — no green-only posture.
    """

    def verify(
        self,
        run_id: str,
        candidate_patch: CandidatePatch,
        measurement_basis: tuple[str, ...],
        observed_gains: tuple[str, ...],
        residual_weaknesses: tuple[str, ...],
    ) -> CandidateVerification:
        """
        Record verification outcome for a candidate patch.

        Raises VerificationError if:
        - candidate_patch is a placeholder
        - measurement_basis is empty
        - observed_gains is empty
        - residual_weaknesses is empty (no green-only posture)
        """
        if candidate_patch.placeholder:
            raise VerificationError(
                "cannot verify a placeholder patch — "
                "run CandidateGenerationService first"
            )

        if not measurement_basis:
            raise VerificationError(
                "measurement_basis must not be empty — "
                "verification without a stated measurement basis cannot be trusted"
            )

        if not observed_gains:
            raise VerificationError(
                "observed_gains must not be empty — "
                "verification must record what improved"
            )

        if not residual_weaknesses:
            raise VerificationError(
                "residual_weaknesses must not be empty — "
                "no green-only posture is permitted; "
                "verification must disclose what remained weak"
            )

        posture = _compute_verification_posture(observed_gains, residual_weaknesses)

        return CandidateVerification(
            run_id=run_id,
            placeholder=False,
            verified_patch_artifact_id=candidate_patch.artifact_id,
            measurement_basis=measurement_basis,
            observed_gains=observed_gains,
            residual_weaknesses=residual_weaknesses,
            verification_posture=posture,
            parent_artifact_ids=(candidate_patch.artifact_id,),
            non_authoritative_notice=(
                "Non-authoritative candidate verification. "
                "Does not claim deterministic upstream truth."
            ),
            summary=(
                f"Verification: posture={posture.value}, "
                f"{len(observed_gains)} gain(s), "
                f"{len(residual_weaknesses)} residual weakness(es)."
            ),
        )


def _compute_verification_posture(
    observed_gains: tuple[str, ...],
    residual_weaknesses: tuple[str, ...],
) -> VerificationPosture:
    """
    Compute verification posture from the balance of gains vs weaknesses.

    STRONG  — gains outnumber weaknesses
    WEAK    — weaknesses outnumber gains
    MIXED   — equal counts (or any tie)
    """
    g = len(observed_gains)
    w = len(residual_weaknesses)
    if g > w:
        return VerificationPosture.STRONG
    if w > g:
        return VerificationPosture.WEAK
    return VerificationPosture.MIXED
