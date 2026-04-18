"""
Reviewability engine for forgeHQ — Phase 5.

Computes the ReviewabilityState for a proposal backbone from its constituent
artifacts. Missing any required backbone artifact forces NOT_REVIEWABLE.

This module is pure — it takes artifact instances and returns a state + reasons
without side effects or persistence.
"""
from app.domain.artifacts.enums import ArtifactFamily
from app.domain.reviewability.enums import NotReviewableReason, ReviewabilityState
from app.schemas.candidate_design import CandidateDesign
from app.schemas.candidate_patch import CandidatePatch
from app.schemas.candidate_verification import CandidateVerification
from app.schemas.context_bundle import ContextBundle
from app.schemas.falsification_report import FalsificationReport
from app.schemas.signal_snapshot import SignalSnapshot
from app.schemas.target_ranking import TargetRanking


def compute_reviewability(
    signal_snapshot: SignalSnapshot,
    target_ranking: TargetRanking,
    context_bundle: ContextBundle,
    candidate_design: CandidateDesign,
    candidate_patch: CandidatePatch,
    falsification_report: FalsificationReport,
    candidate_verification: CandidateVerification,
) -> tuple[ReviewabilityState, tuple[NotReviewableReason, ...]]:
    """
    Compute reviewability state from a complete backbone artifact set.

    Returns (ReviewabilityState, not_reviewable_reasons).
    not_reviewable_reasons is empty when state is REVIEWABLE.

    A proposal is REVIEWABLE only when all conditions are satisfied.
    Missing any condition forces NOT_REVIEWABLE.
    """
    reasons: list[NotReviewableReason] = []

    # Challenge artifact must exist and be non-placeholder.
    if falsification_report.placeholder or not falsification_report.challenged_patch_artifact_id:
        reasons.append(NotReviewableReason.MISSING_CHALLENGE_ARTIFACT)

    # Verification artifact must exist and be non-placeholder.
    if candidate_verification.placeholder or not candidate_verification.verified_patch_artifact_id:
        reasons.append(NotReviewableReason.MISSING_VERIFICATION_ARTIFACT)

    # Signal snapshot must have admitted source refs.
    if not signal_snapshot.admitted_source_refs:
        reasons.append(NotReviewableReason.MISSING_SOURCE_REFS)

    # All backbone artifacts must be non-placeholder (no scope escape from placeholder chain).
    placeholder_artifacts = [
        art
        for art in (
            signal_snapshot,
            target_ranking,
            context_bundle,
            candidate_design,
            candidate_patch,
            falsification_report,
            candidate_verification,
        )
        if art.placeholder
    ]
    if placeholder_artifacts:
        # Only add SCOPE_ESCAPE_DETECTED once even if multiple placeholders.
        if NotReviewableReason.SCOPE_ESCAPE_DETECTED not in reasons:
            reasons.append(NotReviewableReason.SCOPE_ESCAPE_DETECTED)

    # Design must have non-empty scope boundary (explicit scope boundary required).
    if not candidate_design.scope_boundary_statement.strip() or candidate_design.placeholder:
        if NotReviewableReason.SCOPE_ESCAPE_DETECTED not in reasons:
            reasons.append(NotReviewableReason.SCOPE_ESCAPE_DETECTED)

    # Parent refs must form a valid chain (patch must reference design, design must reference bundle).
    if candidate_patch.design_artifact_id != candidate_design.artifact_id:
        if NotReviewableReason.INVALID_PARENT_EVIDENCE_REFS not in reasons:
            reasons.append(NotReviewableReason.INVALID_PARENT_EVIDENCE_REFS)

    # Verification must disclose downgrade factors if falsification was downgraded.
    if (
        falsification_report.downgrade_applied
        and not falsification_report.downgrade_reasons
    ):
        reasons.append(NotReviewableReason.MISSING_DOWNGRADE_FACTORS)

    if reasons:
        return ReviewabilityState.NOT_REVIEWABLE, tuple(reasons)

    return ReviewabilityState.REVIEWABLE, ()
