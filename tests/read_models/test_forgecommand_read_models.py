"""
Tests for ForgeCommandReadModelService — forgeHQ Phase 6.

Covers: queue item shape, detail model shape, layered evidence/challenge/risk
separation, approval blocking when not reviewable, lifecycle/decision separation.
"""
import pytest

from app.domain.reviewability.enums import (
    ChallengePosture,
    NotReviewableReason,
    OperatorDecisionState,
    ProposalLifecycleState,
    ReviewabilityState,
    VerificationPosture,
)
from app.read_models.forgecommand import ProposalDetailModel, ProposalQueueItem
from app.schemas.ranking_factor_trace import RankingFactor
from app.services.candidate_design_service import CandidateDesignService
from app.services.candidate_generation_service import CandidateGenerationService
from app.services.candidate_verification_service import CandidateVerificationService
from app.services.context_bundle_service import ContextBundleService
from app.services.falsification_service import FalsificationService
from app.services.forgecommand_read_model_service import ForgeCommandReadModelService
from app.services.proposal_packaging_service import ProposalPackagingService
from app.services.signal_intake_service import SignalIntakeService
from app.services.target_ranking_service import TargetRankingService


# ---------------------------------------------------------------------------
# Full pipeline + read model helper
# ---------------------------------------------------------------------------

_DESIGN_KWARGS = dict(
    change_hypothesis="Add null-path branch in auth handler",
    intended_confidence_gain="Raise branch coverage to 80%",
    targeted_behaviors=("null input returns 401",),
    oracle_strategy="Run test suite and measure branch coverage",
    disconfirming_checks=("mutation survivors still present",),
    failure_hypotheses=("change breaks integration path",),
)


def _run_pipeline_to_detail(run_id: str = "r1"):
    """Run the full pipeline and return all artifacts needed for read model assembly."""
    snapshot, _ = SignalIntakeService().admit_signals(
        run_id=run_id, source_refs=("forgeeval://coverage/auth",)
    )
    factor = RankingFactor(
        factor_name="coverage_gap", raw_value=0.6, normalized_score=0.6,
        source_ref="forgeeval://coverage/auth", is_deterministic=True,
        explanation="coverage gap",
    )
    ranking, trace = TargetRankingService().rank_target(
        run_id=run_id, target_id="service_a",
        signal_snapshot=snapshot, ranking_factors=(factor,),
    )
    bundle = ContextBundleService().build_context_bundle(
        run_id=run_id, target_id="service_a", target_ranking=ranking,
        context_item_refs=("src/auth.py",),
        scope_boundary_statement="bounded to auth module",
    )
    design = CandidateDesignService().create_design(
        run_id=run_id, context_bundle=bundle, **_DESIGN_KWARGS
    )
    patch = CandidateGenerationService().generate_patch(
        run_id=run_id, candidate_design=design, context_bundle=bundle,
        modified_refs=("src/auth.py",),
    )
    falsification = FalsificationService().challenge(
        run_id=run_id, candidate_patch=patch, candidate_design=design,
        disconfirming_checks_evaluated=("mutation survivors still present",),
    )
    verification = CandidateVerificationService().verify(
        run_id=run_id, candidate_patch=patch,
        measurement_basis=("branch coverage",),
        observed_gains=("null path now covered",),
        residual_weaknesses=("mutation survivors remain",),
    )
    confidence_summary, proposal = ProposalPackagingService().package_proposal(
        run_id=run_id,
        signal_snapshot=snapshot,
        target_ranking=ranking,
        context_bundle=bundle,
        candidate_design=design,
        candidate_patch=patch,
        falsification_report=falsification,
        candidate_verification=verification,
    )
    return dict(
        proposal=proposal,
        signal_snapshot=snapshot,
        target_ranking=ranking,
        ranking_trace=trace,
        context_bundle=bundle,
        candidate_design=design,
        candidate_patch=patch,
        falsification_report=falsification,
        candidate_verification=verification,
        confidence_summary=confidence_summary,
    )


# ---------------------------------------------------------------------------
# Queue item shape
# ---------------------------------------------------------------------------


def test_queue_item_reviewability_state():
    parts = _run_pipeline_to_detail()
    svc = ForgeCommandReadModelService()
    item = svc.build_queue_item(
        proposal=parts["proposal"],
        candidate_design=parts["candidate_design"],
        confidence_summary=parts["confidence_summary"],
    )
    assert item.reviewability_state == ReviewabilityState.REVIEWABLE


def test_queue_item_approval_available_when_reviewable():
    parts = _run_pipeline_to_detail()
    svc = ForgeCommandReadModelService()
    item = svc.build_queue_item(
        proposal=parts["proposal"],
        candidate_design=parts["candidate_design"],
        confidence_summary=parts["confidence_summary"],
    )
    assert item.approval_actions_available is True


def test_queue_item_operator_decision_state_is_no_decision():
    parts = _run_pipeline_to_detail()
    svc = ForgeCommandReadModelService()
    item = svc.build_queue_item(
        proposal=parts["proposal"],
        candidate_design=parts["candidate_design"],
        confidence_summary=parts["confidence_summary"],
    )
    assert item.operator_decision_state == OperatorDecisionState.NO_DECISION


def test_queue_item_lifecycle_state_is_packaged():
    parts = _run_pipeline_to_detail()
    svc = ForgeCommandReadModelService()
    item = svc.build_queue_item(
        proposal=parts["proposal"],
        candidate_design=parts["candidate_design"],
        confidence_summary=parts["confidence_summary"],
    )
    assert item.proposal_lifecycle_state == ProposalLifecycleState.PACKAGED


# ---------------------------------------------------------------------------
# Detail model shape and layered separation
# ---------------------------------------------------------------------------


def test_detail_model_is_correct_type():
    parts = _run_pipeline_to_detail()
    svc = ForgeCommandReadModelService()
    detail = svc.build_detail_model(**parts)
    assert isinstance(detail, ProposalDetailModel)


def test_detail_model_evidence_layer_has_admitted_refs():
    parts = _run_pipeline_to_detail()
    svc = ForgeCommandReadModelService()
    detail = svc.build_detail_model(**parts)
    assert "forgeeval://coverage/auth" in detail.evidence.admitted_source_refs


def test_detail_model_rationale_layer_has_change_hypothesis():
    parts = _run_pipeline_to_detail()
    svc = ForgeCommandReadModelService()
    detail = svc.build_detail_model(**parts)
    assert detail.rationale.change_hypothesis == _DESIGN_KWARGS["change_hypothesis"]


def test_detail_model_challenge_layer_has_posture():
    parts = _run_pipeline_to_detail()
    svc = ForgeCommandReadModelService()
    detail = svc.build_detail_model(**parts)
    assert detail.challenge.challenge_posture == ChallengePosture.PASSED


def test_detail_model_risk_layer_has_residual_weaknesses():
    parts = _run_pipeline_to_detail()
    svc = ForgeCommandReadModelService()
    detail = svc.build_detail_model(**parts)
    assert len(detail.risk.residual_weaknesses) >= 1


def test_detail_model_risk_layer_has_observed_gains():
    parts = _run_pipeline_to_detail()
    svc = ForgeCommandReadModelService()
    detail = svc.build_detail_model(**parts)
    assert len(detail.risk.observed_gains) >= 1


def test_detail_model_layers_are_separate_attributes():
    parts = _run_pipeline_to_detail()
    svc = ForgeCommandReadModelService()
    detail = svc.build_detail_model(**parts)
    # Each layer is an independent typed object — not collapsed into a single field.
    assert hasattr(detail, "evidence")
    assert hasattr(detail, "rationale")
    assert hasattr(detail, "challenge")
    assert hasattr(detail, "risk")


# ---------------------------------------------------------------------------
# Approval blocking when not reviewable
# ---------------------------------------------------------------------------


def test_approval_blocked_for_not_reviewable_proposal():
    """Build a proposal with a placeholder falsification to force NOT_REVIEWABLE."""
    from app.schemas.falsification_report import FalsificationReport
    from app.services.reviewability_engine import compute_reviewability

    parts = _run_pipeline_to_detail()
    # Construct a NOT_REVIEWABLE proposal directly by patching the reviewability.
    # We test the queue item service with a proposal that has NOT_REVIEWABLE state.
    from dataclasses import replace

    not_reviewable_proposal = replace(
        parts["proposal"],
        reviewability_state=ReviewabilityState.NOT_REVIEWABLE,
        not_reviewable_reasons=(NotReviewableReason.MISSING_CHALLENGE_ARTIFACT,),
    )

    svc = ForgeCommandReadModelService()
    item = svc.build_queue_item(
        proposal=not_reviewable_proposal,
        candidate_design=parts["candidate_design"],
        confidence_summary=parts["confidence_summary"],
    )
    assert item.approval_actions_available is False


def test_approval_blocked_reason_is_set_in_detail_model():
    """Detail model exposes why approval is blocked."""
    from dataclasses import replace

    parts = _run_pipeline_to_detail()
    not_reviewable_proposal = replace(
        parts["proposal"],
        reviewability_state=ReviewabilityState.NOT_REVIEWABLE,
        not_reviewable_reasons=(NotReviewableReason.MISSING_CHALLENGE_ARTIFACT,),
    )

    svc = ForgeCommandReadModelService()
    detail_parts = {**parts, "proposal": not_reviewable_proposal}
    detail = svc.build_detail_model(**detail_parts)

    assert detail.approval_actions_available is False
    assert detail.approval_blocked_reason is not None
    assert "not reviewable" in detail.approval_blocked_reason.lower()


def test_approval_blocked_reason_is_none_when_reviewable():
    parts = _run_pipeline_to_detail()
    svc = ForgeCommandReadModelService()
    detail = svc.build_detail_model(**parts)
    assert detail.approval_blocked_reason is None


# ---------------------------------------------------------------------------
# Non-authoritative notice always present
# ---------------------------------------------------------------------------


def test_detail_model_non_authoritative_notice_present():
    parts = _run_pipeline_to_detail()
    svc = ForgeCommandReadModelService()
    detail = svc.build_detail_model(**parts)
    assert detail.non_authoritative_notice
    assert "non-authoritative" in detail.non_authoritative_notice.lower()


# ---------------------------------------------------------------------------
# Lifecycle / decision separation in detail model
# ---------------------------------------------------------------------------


def test_detail_model_lifecycle_and_decision_are_separate():
    parts = _run_pipeline_to_detail()
    svc = ForgeCommandReadModelService()
    detail = svc.build_detail_model(**parts)
    assert detail.proposal_lifecycle_state == ProposalLifecycleState.PACKAGED
    assert detail.operator_decision_state == OperatorDecisionState.NO_DECISION
    assert detail.proposal_lifecycle_state != detail.operator_decision_state
