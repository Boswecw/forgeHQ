"""
Proposal packaging service for forgeHQ — Stage 8.

Assembles the confidence shaping summary and final proposal artifact from
the complete backbone, computes reviewability state, and persists lineage.

Hard rules:
- All seven backbone artifacts must be non-placeholder.
- Reviewability is computed — not assumed.
- Proposal lifecycle state is separate from operator decision state.
- Missing backbone artifacts force NOT_REVIEWABLE — never silently pass.
- DataForge persistence wiring is pending Phase 5 DataForge integration;
  the persistence stubs record the state in-memory.
"""
from app.domain.artifacts.enums import ArtifactFamily, LineageLayer
from app.domain.reviewability.enums import (
    OperatorDecisionState,
    ProposalLifecycleState,
    ReviewabilityState,
)
from app.persistence.artifact_registry import ArtifactRegistry
from app.persistence.lineage_repository import LineageRepository
from app.persistence.proposal_repository import ProposalRepository, ProposalRow
from app.schemas.candidate_design import CandidateDesign
from app.schemas.candidate_patch import CandidatePatch
from app.schemas.candidate_verification import CandidateVerification
from app.schemas.confidence_shaping_summary import ConfidenceShapingSummary
from app.schemas.context_bundle import ContextBundle
from app.schemas.falsification_report import FalsificationReport
from app.schemas.forgehq_proposal import ForgeHQProposal
from app.schemas.signal_snapshot import SignalSnapshot
from app.schemas.target_ranking import TargetRanking
from app.services.reviewability_engine import compute_reviewability


class PackagingError(ValueError):
    """Raised when proposal packaging cannot proceed safely."""


class ProposalPackagingService:
    """
    Assembles the final proposal package from the complete backbone.

    Returns (ConfidenceShapingSummary, ForgeHQProposal) with
    placeholder=False and computed reviewability state.

    Optionally persists the backbone and proposal through injected
    persistence stubs (ArtifactRegistry, LineageRepository, ProposalRepository).
    """

    def __init__(
        self,
        artifact_registry: ArtifactRegistry | None = None,
        lineage_repository: LineageRepository | None = None,
        proposal_repository: ProposalRepository | None = None,
    ) -> None:
        self._registry = artifact_registry or ArtifactRegistry()
        self._lineage = lineage_repository or LineageRepository()
        self._proposals = proposal_repository or ProposalRepository()

    def package_proposal(
        self,
        run_id: str,
        signal_snapshot: SignalSnapshot,
        target_ranking: TargetRanking,
        context_bundle: ContextBundle,
        candidate_design: CandidateDesign,
        candidate_patch: CandidatePatch,
        falsification_report: FalsificationReport,
        candidate_verification: CandidateVerification,
    ) -> tuple[ConfidenceShapingSummary, ForgeHQProposal]:
        """
        Assemble and persist the final proposal from the backbone artifacts.

        Computes reviewability state. Persists backbone artifacts, lineage
        edges, and the proposal row.

        Raises PackagingError if any backbone artifact is a placeholder.
        """
        backbone = (
            signal_snapshot,
            target_ranking,
            context_bundle,
            candidate_design,
            candidate_patch,
            falsification_report,
            candidate_verification,
        )

        placeholder_families = [
            art.artifact_family.value for art in backbone if art.placeholder
        ]
        if placeholder_families:
            raise PackagingError(
                f"cannot package a proposal with placeholder backbone artifacts: "
                f"{placeholder_families} — run all upstream services first"
            )

        reviewability_state, not_reviewable_reasons = compute_reviewability(
            signal_snapshot=signal_snapshot,
            target_ranking=target_ranking,
            context_bundle=context_bundle,
            candidate_design=candidate_design,
            candidate_patch=candidate_patch,
            falsification_report=falsification_report,
            candidate_verification=candidate_verification,
        )

        downgrade_factors = falsification_report.downgrade_reasons if falsification_report.downgrade_applied else ()

        narrative = _build_confidence_narrative(
            reviewability_state=reviewability_state,
            challenge_posture=falsification_report.challenge_posture,
            verification_posture=candidate_verification.verification_posture,
            downgrade_factors=downgrade_factors,
        )

        confidence_summary = ConfidenceShapingSummary(
            run_id=run_id,
            placeholder=False,
            falsification_artifact_id=falsification_report.artifact_id,
            verification_artifact_id=candidate_verification.artifact_id,
            challenge_posture=falsification_report.challenge_posture,
            verification_posture=candidate_verification.verification_posture,
            downgrade_factors=downgrade_factors,
            overall_confidence_narrative=narrative,
            parent_artifact_ids=(
                falsification_report.artifact_id,
                candidate_verification.artifact_id,
            ),
            non_authoritative_notice=(
                "Non-authoritative confidence summary. "
                "Does not claim deterministic upstream truth."
            ),
            summary=(
                f"Confidence summary: challenge={falsification_report.challenge_posture.value}, "
                f"verification={candidate_verification.verification_posture.value}."
            ),
        )

        backbone_ids = tuple(art.artifact_id for art in backbone) + (confidence_summary.artifact_id,)

        proposal = ForgeHQProposal(
            run_id=run_id,
            placeholder=False,
            confidence_summary_artifact_id=confidence_summary.artifact_id,
            backbone_artifact_ids=backbone_ids,
            reviewability_state=reviewability_state,
            not_reviewable_reasons=not_reviewable_reasons,
            proposal_lifecycle_state=ProposalLifecycleState.PACKAGED,
            operator_decision_state=OperatorDecisionState.NO_DECISION,
            parent_artifact_ids=(confidence_summary.artifact_id,),
            non_authoritative_notice=(
                "Non-authoritative forgeHQ proposal. "
                "Does not claim deterministic upstream truth. "
                "Requires human operator review."
            ),
            summary=(
                f"Proposal for target '{candidate_design.target_id}': "
                f"reviewability={reviewability_state.value}. "
                "Non-authoritative — awaiting operator review."
            ),
        )

        # Persist backbone through stubs (DataForge wiring pending).
        for art in backbone:
            self._registry.register(art)
        self._registry.register(confidence_summary)
        self._registry.register(proposal)

        _record_lineage(self._lineage, backbone, confidence_summary, proposal)

        self._proposals.save(
            ProposalRow(
                run_id=run_id,
                proposal_artifact_id=proposal.artifact_id,
                reviewability_state=reviewability_state,
                proposal_lifecycle_state=ProposalLifecycleState.PACKAGED,
                operator_decision_state=OperatorDecisionState.NO_DECISION,
            )
        )

        return confidence_summary, proposal


def _build_confidence_narrative(
    reviewability_state: ReviewabilityState,
    challenge_posture,
    verification_posture,
    downgrade_factors: tuple[str, ...],
) -> str:
    parts = [
        f"Candidate challenge posture: {challenge_posture.value}.",
        f"Candidate verification posture: {verification_posture.value}.",
    ]
    if downgrade_factors:
        parts.append(
            f"Downgrade applied: {len(downgrade_factors)} factor(s) identified."
        )
    parts.append(
        f"Reviewability state: {reviewability_state.value}. "
        "Non-authoritative — human operator review required."
    )
    return " ".join(parts)


def _record_lineage(
    lineage: LineageRepository,
    backbone,
    confidence_summary: ConfidenceShapingSummary,
    proposal: ForgeHQProposal,
) -> None:
    """Record non-authoritative proposal lineage edges for the backbone."""
    layer = LineageLayer.NON_AUTHORITATIVE_PROPOSAL

    # Record parent→child edges declared in each backbone artifact.
    for art in backbone:
        for parent_id in art.parent_artifact_ids:
            lineage.record_edge(
                parent_artifact_id=parent_id,
                child_artifact_id=art.artifact_id,
                layer=layer,
            )

    # Confidence summary → proposal
    lineage.record_edge(
        parent_artifact_id=confidence_summary.artifact_id,
        child_artifact_id=proposal.artifact_id,
        layer=layer,
    )
