"""
ForgeCommand read model service for forgeHQ — Phase 6.

Assembles queue items and detail models from persisted backbone artifacts for
the ForgeCommand operator review surface.

Hard rules:
- Approval actions are blocked when reviewability_state is NOT_REVIEWABLE.
- Evidence, rationale, challenge, and risk layers must remain separate.
- Proposal lifecycle state and operator decision state must never be collapsed.
- Read models are non-authoritative — they present proposals, not facts.
"""
from app.domain.reviewability.enums import ReviewabilityState
from app.read_models.forgecommand import (
    ChallengeLayer,
    EvidenceLayer,
    ProposalDetailModel,
    ProposalQueueItem,
    RationaleLayer,
    RiskLayer,
)
from app.schemas.candidate_design import CandidateDesign
from app.schemas.candidate_patch import CandidatePatch
from app.schemas.candidate_verification import CandidateVerification
from app.schemas.confidence_shaping_summary import ConfidenceShapingSummary
from app.schemas.context_bundle import ContextBundle
from app.schemas.falsification_report import FalsificationReport
from app.schemas.forgehq_proposal import ForgeHQProposal
from app.schemas.ranking_factor_trace import RankingFactorTrace
from app.schemas.signal_snapshot import SignalSnapshot
from app.schemas.target_ranking import TargetRanking


_NON_AUTHORITATIVE_NOTICE = (
    "This proposal is non-authoritative. "
    "forgeHQ proposes and evaluates candidates; it does not mint canonical truth. "
    "Human operator review and decision are required."
)

_APPROVAL_BLOCKED_NOT_REVIEWABLE = (
    "Approval actions are unavailable: this proposal is not reviewable. "
    "One or more required backbone conditions are unmet. "
    "See not_reviewable_reasons for details."
)


class ForgeCommandReadModelService:
    """
    Assembles ForgeCommand read models from backbone artifacts.

    Returns ProposalQueueItem (list surface) and ProposalDetailModel (detail surface).
    Approval actions are blocked when reviewability_state is NOT_REVIEWABLE.
    """

    def build_queue_item(
        self,
        proposal: ForgeHQProposal,
        candidate_design: CandidateDesign,
        confidence_summary: ConfidenceShapingSummary,
    ) -> ProposalQueueItem:
        """Assemble a queue list item from the proposal and its summary."""
        approval_available = proposal.reviewability_state == ReviewabilityState.REVIEWABLE

        return ProposalQueueItem(
            proposal_artifact_id=proposal.artifact_id,
            run_id=proposal.run_id,
            target_id=candidate_design.target_id,
            change_hypothesis=candidate_design.change_hypothesis,
            reviewability_state=proposal.reviewability_state,
            proposal_lifecycle_state=proposal.proposal_lifecycle_state,
            operator_decision_state=proposal.operator_decision_state,
            challenge_posture=confidence_summary.challenge_posture,
            verification_posture=confidence_summary.verification_posture,
            summary=proposal.summary,
            approval_actions_available=approval_available,
        )

    def build_detail_model(
        self,
        proposal: ForgeHQProposal,
        signal_snapshot: SignalSnapshot,
        target_ranking: TargetRanking,
        ranking_trace: RankingFactorTrace,
        context_bundle: ContextBundle,
        candidate_design: CandidateDesign,
        candidate_patch: CandidatePatch,
        falsification_report: FalsificationReport,
        candidate_verification: CandidateVerification,
        confidence_summary: ConfidenceShapingSummary,
    ) -> ProposalDetailModel:
        """Assemble the full layered detail model for the ForgeCommand review surface."""
        approval_available = proposal.reviewability_state == ReviewabilityState.REVIEWABLE
        blocked_reason = None if approval_available else _APPROVAL_BLOCKED_NOT_REVIEWABLE

        evidence = EvidenceLayer(
            admitted_source_refs=signal_snapshot.admitted_source_refs,
            target_id=target_ranking.ranked_target_id,
            composite_ranking_score=target_ranking.composite_score,
            ranking_factor_count=len(ranking_trace.factors),
        )

        rationale = RationaleLayer(
            change_hypothesis=candidate_design.change_hypothesis,
            intended_confidence_gain=candidate_design.intended_confidence_gain,
            targeted_behaviors=candidate_design.targeted_behaviors,
            oracle_strategy=candidate_design.oracle_strategy,
            scope_boundary_statement=candidate_design.scope_boundary_statement,
            modified_refs=candidate_patch.modified_refs,
        )

        challenge = ChallengeLayer(
            challenge_posture=falsification_report.challenge_posture,
            downgrade_applied=falsification_report.downgrade_applied,
            contradictions=falsification_report.contradictions,
            duplicate_test_warnings=falsification_report.duplicate_test_warnings,
            shallow_gain_indicators=falsification_report.shallow_gain_indicators,
            residual_concerns=falsification_report.residual_concerns,
            disconfirming_checks_evaluated=falsification_report.disconfirming_checks_evaluated,
        )

        risk = RiskLayer(
            verification_posture=candidate_verification.verification_posture,
            observed_gains=candidate_verification.observed_gains,
            residual_weaknesses=candidate_verification.residual_weaknesses,
            measurement_basis=candidate_verification.measurement_basis,
            failure_hypotheses=candidate_design.failure_hypotheses,
            disconfirming_checks=candidate_design.disconfirming_checks,
        )

        return ProposalDetailModel(
            proposal_artifact_id=proposal.artifact_id,
            run_id=proposal.run_id,
            reviewability_state=proposal.reviewability_state,
            not_reviewable_reasons=proposal.not_reviewable_reasons,
            proposal_lifecycle_state=proposal.proposal_lifecycle_state,
            operator_decision_state=proposal.operator_decision_state,
            approval_actions_available=approval_available,
            approval_blocked_reason=blocked_reason,
            evidence=evidence,
            rationale=rationale,
            challenge=challenge,
            risk=risk,
            overall_confidence_narrative=confidence_summary.overall_confidence_narrative,
            non_authoritative_notice=_NON_AUTHORITATIVE_NOTICE,
        )
