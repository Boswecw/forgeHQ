"""
Tests for ProposalPackagingService, ReviewabilityEngine, and persistence stubs
— forgeHQ Phase 5.

Covers: full backbone packaging, reviewability computation, lifecycle/decision
separation, lineage edge persistence, and not_reviewable conditions.
"""
import pytest

from app.domain.artifacts.enums import ArtifactFamily, LineageLayer
from app.domain.reviewability.enums import (
    OperatorDecisionState,
    ProposalLifecycleState,
    ReviewabilityState,
)
from app.persistence.artifact_registry import ArtifactRegistry
from app.persistence.lineage_repository import LineageRepository
from app.persistence.proposal_repository import ProposalRepository
from app.schemas.ranking_factor_trace import RankingFactor
from app.services.candidate_design_service import CandidateDesignService
from app.services.candidate_generation_service import CandidateGenerationService
from app.services.candidate_verification_service import CandidateVerificationService
from app.services.context_bundle_service import ContextBundleService
from app.services.falsification_service import FalsificationService
from app.services.proposal_packaging_service import PackagingError, ProposalPackagingService
from app.services.signal_intake_service import SignalIntakeService
from app.services.target_ranking_service import TargetRankingService


# ---------------------------------------------------------------------------
# Full pipeline helper
# ---------------------------------------------------------------------------

_DESIGN_KWARGS = dict(
    change_hypothesis="Add null-path branch in auth handler",
    intended_confidence_gain="Raise branch coverage to 80%",
    targeted_behaviors=("null input returns 401",),
    oracle_strategy="Run test suite and measure branch coverage",
    disconfirming_checks=("mutation survivors still present",),
    failure_hypotheses=("change breaks integration path",),
)


def _run_full_pipeline(run_id: str = "r1"):
    """Run the complete 8-stage pipeline and return all backbone artifacts."""
    # Stage 1
    snapshot, _ = SignalIntakeService().admit_signals(
        run_id=run_id, source_refs=("forgeeval://coverage/auth",)
    )
    # Stage 2
    factor = RankingFactor(
        factor_name="coverage_gap", raw_value=0.6, normalized_score=0.6,
        source_ref="forgeeval://coverage/auth", is_deterministic=True,
        explanation="coverage gap",
    )
    ranking, _ = TargetRankingService().rank_target(
        run_id=run_id, target_id="service_a",
        signal_snapshot=snapshot, ranking_factors=(factor,),
    )
    # Stage 3
    bundle = ContextBundleService().build_context_bundle(
        run_id=run_id, target_id="service_a", target_ranking=ranking,
        context_item_refs=("src/auth.py",),
        scope_boundary_statement="bounded to auth module",
    )
    # Stage 4
    design = CandidateDesignService().create_design(
        run_id=run_id, context_bundle=bundle, **_DESIGN_KWARGS
    )
    # Stage 5
    patch = CandidateGenerationService().generate_patch(
        run_id=run_id, candidate_design=design, context_bundle=bundle,
        modified_refs=("src/auth.py",),
    )
    # Stage 6
    falsification = FalsificationService().challenge(
        run_id=run_id, candidate_patch=patch, candidate_design=design,
        disconfirming_checks_evaluated=("mutation survivors still present",),
    )
    # Stage 7
    verification = CandidateVerificationService().verify(
        run_id=run_id, candidate_patch=patch,
        measurement_basis=("branch coverage",),
        observed_gains=("null path now covered",),
        residual_weaknesses=("mutation survivors remain",),
    )
    return snapshot, ranking, bundle, design, patch, falsification, verification


def _package(svc: ProposalPackagingService, backbone, run_id: str = "r1"):
    """Unpack backbone tuple and call package_proposal with explicit kwargs."""
    snapshot, ranking, bundle, design, patch, falsification, verification = backbone
    return svc.package_proposal(
        run_id=run_id,
        signal_snapshot=snapshot,
        target_ranking=ranking,
        context_bundle=bundle,
        candidate_design=design,
        candidate_patch=patch,
        falsification_report=falsification,
        candidate_verification=verification,
    )


# ---------------------------------------------------------------------------
# Full backbone packaging
# ---------------------------------------------------------------------------


def test_full_backbone_produces_reviewable_proposal():
    backbone = _run_full_pipeline()
    snapshot, ranking, bundle, design, patch, falsification, verification = backbone

    registry = ArtifactRegistry()
    lineage = LineageRepository()
    proposals = ProposalRepository()
    svc = ProposalPackagingService(registry, lineage, proposals)

    _, proposal = svc.package_proposal(
        run_id="r1",
        signal_snapshot=snapshot,
        target_ranking=ranking,
        context_bundle=bundle,
        candidate_design=design,
        candidate_patch=patch,
        falsification_report=falsification,
        candidate_verification=verification,
    )

    assert proposal.reviewability_state == ReviewabilityState.REVIEWABLE
    assert proposal.not_reviewable_reasons == ()


def test_proposal_artifact_family():
    backbone = _run_full_pipeline()
    svc = ProposalPackagingService()
    _, proposal = _package(svc, backbone)
    assert proposal.artifact_family == ArtifactFamily.FORGEHQ_PROPOSAL


def test_confidence_summary_artifact_family():
    backbone = _run_full_pipeline()
    svc = ProposalPackagingService()
    summary, _ = _package(svc, backbone)
    assert summary.artifact_family == ArtifactFamily.CONFIDENCE_SHAPING_SUMMARY


def test_proposal_is_not_placeholder():
    backbone = _run_full_pipeline()
    svc = ProposalPackagingService()
    _, proposal = _package(svc, backbone)
    assert proposal.placeholder is False


# ---------------------------------------------------------------------------
# Fail-closed: placeholder backbone
# ---------------------------------------------------------------------------


def test_placeholder_backbone_artifact_raises_packaging_error():
    from app.schemas.signal_snapshot import SignalSnapshot

    backbone = _run_full_pipeline()
    snapshot, ranking, bundle, design, patch, falsification, verification = backbone
    placeholder_snapshot = SignalSnapshot(run_id="r1")

    svc = ProposalPackagingService()
    with pytest.raises(PackagingError, match="placeholder"):
        svc.package_proposal(
            run_id="r1",
            signal_snapshot=placeholder_snapshot,  # placeholder!
            target_ranking=ranking,
            context_bundle=bundle,
            candidate_design=design,
            candidate_patch=patch,
            falsification_report=falsification,
            candidate_verification=verification,
        )


# ---------------------------------------------------------------------------
# NOT_REVIEWABLE: missing challenge
# ---------------------------------------------------------------------------


def test_placeholder_falsification_yields_not_reviewable():
    from app.schemas.falsification_report import FalsificationReport

    backbone = _run_full_pipeline()
    snapshot, ranking, bundle, design, patch, _, verification = backbone
    placeholder_falsification = FalsificationReport(run_id="r1")
    # Can't package placeholder — packaging service rejects it.
    # So test via reviewability_engine directly.
    from app.services.reviewability_engine import compute_reviewability

    state, reasons = compute_reviewability(
        signal_snapshot=snapshot,
        target_ranking=ranking,
        context_bundle=bundle,
        candidate_design=design,
        candidate_patch=patch,
        falsification_report=placeholder_falsification,
        candidate_verification=verification,
    )
    assert state == ReviewabilityState.NOT_REVIEWABLE
    from app.domain.reviewability.enums import NotReviewableReason
    assert NotReviewableReason.MISSING_CHALLENGE_ARTIFACT in reasons


# ---------------------------------------------------------------------------
# NOT_REVIEWABLE: missing verification
# ---------------------------------------------------------------------------


def test_placeholder_verification_yields_not_reviewable():
    from app.schemas.candidate_verification import CandidateVerification
    from app.services.reviewability_engine import compute_reviewability

    backbone = _run_full_pipeline()
    snapshot, ranking, bundle, design, patch, falsification, _ = backbone
    placeholder_verification = CandidateVerification(run_id="r1")

    state, reasons = compute_reviewability(
        signal_snapshot=snapshot,
        target_ranking=ranking,
        context_bundle=bundle,
        candidate_design=design,
        candidate_patch=patch,
        falsification_report=falsification,
        candidate_verification=placeholder_verification,
    )
    assert state == ReviewabilityState.NOT_REVIEWABLE
    from app.domain.reviewability.enums import NotReviewableReason
    assert NotReviewableReason.MISSING_VERIFICATION_ARTIFACT in reasons


# ---------------------------------------------------------------------------
# Lifecycle vs. operator decision separation
# ---------------------------------------------------------------------------


def test_proposal_lifecycle_state_is_packaged():
    backbone = _run_full_pipeline()
    svc = ProposalPackagingService()
    _, proposal = _package(svc, backbone)
    assert proposal.proposal_lifecycle_state == ProposalLifecycleState.PACKAGED


def test_operator_decision_state_is_no_decision():
    backbone = _run_full_pipeline()
    svc = ProposalPackagingService()
    _, proposal = _package(svc, backbone)
    assert proposal.operator_decision_state == OperatorDecisionState.NO_DECISION


def test_lifecycle_and_decision_are_separate_fields():
    backbone = _run_full_pipeline()
    svc = ProposalPackagingService()
    _, proposal = _package(svc, backbone)
    # The two state fields must exist independently — the values must differ
    # in this case (packaged != no_decision shows they're not the same field).
    assert proposal.proposal_lifecycle_state != proposal.operator_decision_state


def test_proposal_row_lifecycle_decision_separation():
    """Verify persistence row preserves separate lifecycle and decision fields."""
    backbone = _run_full_pipeline()
    registry = ArtifactRegistry()
    lineage = LineageRepository()
    proposals = ProposalRepository()
    svc = ProposalPackagingService(registry, lineage, proposals)

    _, proposal = _package(svc, backbone)
    row = proposals.get(proposal.artifact_id)

    assert row is not None
    assert row.proposal_lifecycle_state == ProposalLifecycleState.PACKAGED
    assert row.operator_decision_state == OperatorDecisionState.NO_DECISION


# ---------------------------------------------------------------------------
# Lineage edge persistence
# ---------------------------------------------------------------------------


def test_lineage_edges_are_recorded():
    backbone = _run_full_pipeline()
    registry = ArtifactRegistry()
    lineage = LineageRepository()
    proposals = ProposalRepository()
    svc = ProposalPackagingService(registry, lineage, proposals)

    _package(svc, backbone)
    assert lineage.count() > 0


def test_lineage_edges_use_non_authoritative_layer():
    backbone = _run_full_pipeline()
    lineage = LineageRepository()
    svc = ProposalPackagingService(lineage_repository=lineage)
    _package(svc, backbone)

    for edge in lineage.all_edges():
        assert edge.layer == LineageLayer.NON_AUTHORITATIVE_PROPOSAL


def test_backbone_artifacts_registered():
    backbone = _run_full_pipeline()
    registry = ArtifactRegistry()
    svc = ProposalPackagingService(artifact_registry=registry)

    _, proposal = _package(svc, backbone)

    # All 7 backbone + confidence_summary + proposal = 9 artifacts minimum.
    assert registry.count() >= 9


def test_proposal_registered_in_registry():
    backbone = _run_full_pipeline()
    registry = ArtifactRegistry()
    svc = ProposalPackagingService(artifact_registry=registry)

    _, proposal = _package(svc, backbone)
    assert registry.get(proposal.artifact_id) is not None


# ---------------------------------------------------------------------------
# Backbone artifact IDs preserved in proposal
# ---------------------------------------------------------------------------


def test_backbone_artifact_ids_in_proposal():
    backbone = _run_full_pipeline()
    snapshot, ranking, bundle, design, patch, falsification, verification = backbone
    svc = ProposalPackagingService()

    _, proposal = _package(svc, backbone)

    assert snapshot.artifact_id in proposal.backbone_artifact_ids
    assert patch.artifact_id in proposal.backbone_artifact_ids
    assert falsification.artifact_id in proposal.backbone_artifact_ids
    assert verification.artifact_id in proposal.backbone_artifact_ids
