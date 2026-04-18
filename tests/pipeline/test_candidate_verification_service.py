"""
Tests for CandidateVerificationService — forgeHQ Phase 4.

Covers: fail-closed on placeholder patches, empty measurement basis,
empty gains, empty weaknesses (no green-only posture), verification posture
computation, and non-authoritative posture requirements.
"""
import pytest

from app.domain.artifacts.enums import ArtifactAuthorityPosture, ArtifactFamily
from app.domain.reviewability.enums import VerificationPosture
from app.schemas.ranking_factor_trace import RankingFactor
from app.services.candidate_design_service import CandidateDesignService
from app.services.candidate_generation_service import CandidateGenerationService
from app.services.candidate_verification_service import (
    CandidateVerificationService,
    VerificationError,
)
from app.services.context_bundle_service import ContextBundleService
from app.services.signal_intake_service import SignalIntakeService
from app.services.target_ranking_service import TargetRankingService


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_DESIGN_KWARGS = dict(
    change_hypothesis="Add null-path branch in auth handler",
    intended_confidence_gain="Raise branch coverage to 80%",
    targeted_behaviors=("null input returns 401",),
    oracle_strategy="Run test suite and measure branch coverage",
    disconfirming_checks=("mutation survivors still present",),
    failure_hypotheses=("change breaks integration path",),
)


def _real_patch(run_id: str = "r1"):
    snapshot = SignalIntakeService().admit_signals(
        run_id=run_id, source_refs=("forgeeval://coverage/auth",)
    )[0]
    factor = RankingFactor(
        factor_name="coverage_gap", raw_value=0.6, normalized_score=0.6,
        source_ref="forgeeval://coverage/auth", is_deterministic=True,
        explanation="coverage gap",
    )
    ranking, _ = TargetRankingService().rank_target(
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
    return CandidateGenerationService().generate_patch(
        run_id=run_id, candidate_design=design, context_bundle=bundle,
        modified_refs=("src/auth.py",),
    )


# ---------------------------------------------------------------------------
# Fail-closed: placeholder patch
# ---------------------------------------------------------------------------


def test_placeholder_patch_raises_verification_error():
    from app.schemas.candidate_patch import CandidatePatch

    svc = CandidateVerificationService()
    with pytest.raises(VerificationError, match="placeholder"):
        svc.verify(
            run_id="r1",
            candidate_patch=CandidatePatch(run_id="r1"),
            measurement_basis=("branch coverage",),
            observed_gains=("null path now covered",),
            residual_weaknesses=("mutation survivors remain",),
        )


# ---------------------------------------------------------------------------
# Fail-closed: empty measurement basis
# ---------------------------------------------------------------------------


def test_empty_measurement_basis_raises_verification_error():
    patch = _real_patch()
    svc = CandidateVerificationService()

    with pytest.raises(VerificationError, match="measurement_basis"):
        svc.verify(
            run_id="r1",
            candidate_patch=patch,
            measurement_basis=(),
            observed_gains=("null path now covered",),
            residual_weaknesses=("mutation survivors remain",),
        )


# ---------------------------------------------------------------------------
# Fail-closed: empty observed gains
# ---------------------------------------------------------------------------


def test_empty_observed_gains_raises_verification_error():
    patch = _real_patch()
    svc = CandidateVerificationService()

    with pytest.raises(VerificationError, match="observed_gains"):
        svc.verify(
            run_id="r1",
            candidate_patch=patch,
            measurement_basis=("branch coverage",),
            observed_gains=(),
            residual_weaknesses=("mutation survivors remain",),
        )


# ---------------------------------------------------------------------------
# Fail-closed: no green-only posture
# ---------------------------------------------------------------------------


def test_empty_residual_weaknesses_raises_verification_error():
    patch = _real_patch()
    svc = CandidateVerificationService()

    with pytest.raises(VerificationError, match="residual_weaknesses"):
        svc.verify(
            run_id="r1",
            candidate_patch=patch,
            measurement_basis=("branch coverage",),
            observed_gains=("null path now covered",),
            residual_weaknesses=(),
        )


# ---------------------------------------------------------------------------
# Verification posture computation
# ---------------------------------------------------------------------------


def test_more_gains_than_weaknesses_yields_strong_posture():
    patch = _real_patch()
    svc = CandidateVerificationService()

    result = svc.verify(
        run_id="r1",
        candidate_patch=patch,
        measurement_basis=("branch coverage",),
        observed_gains=("gain A", "gain B", "gain C"),
        residual_weaknesses=("weakness X",),
    )
    assert result.verification_posture == VerificationPosture.STRONG


def test_more_weaknesses_than_gains_yields_weak_posture():
    patch = _real_patch()
    svc = CandidateVerificationService()

    result = svc.verify(
        run_id="r1",
        candidate_patch=patch,
        measurement_basis=("branch coverage",),
        observed_gains=("gain A",),
        residual_weaknesses=("weakness X", "weakness Y", "weakness Z"),
    )
    assert result.verification_posture == VerificationPosture.WEAK


def test_equal_gains_and_weaknesses_yields_mixed_posture():
    patch = _real_patch()
    svc = CandidateVerificationService()

    result = svc.verify(
        run_id="r1",
        candidate_patch=patch,
        measurement_basis=("branch coverage",),
        observed_gains=("gain A", "gain B"),
        residual_weaknesses=("weakness X", "weakness Y"),
    )
    assert result.verification_posture == VerificationPosture.MIXED


# ---------------------------------------------------------------------------
# Gain and limitation recording
# ---------------------------------------------------------------------------


def test_observed_gains_and_weaknesses_preserved():
    patch = _real_patch()
    svc = CandidateVerificationService()
    gains = ("null path now covered", "branch count +3")
    weaknesses = ("mutation survivors remain", "integration test not updated")

    result = svc.verify(
        run_id="r1",
        candidate_patch=patch,
        measurement_basis=("branch coverage", "mutation score"),
        observed_gains=gains,
        residual_weaknesses=weaknesses,
    )
    assert result.observed_gains == gains
    assert result.residual_weaknesses == weaknesses


def test_measurement_basis_preserved():
    patch = _real_patch()
    svc = CandidateVerificationService()
    basis = ("branch coverage", "mutation score")

    result = svc.verify(
        run_id="r1",
        candidate_patch=patch,
        measurement_basis=basis,
        observed_gains=("gain A",),
        residual_weaknesses=("weakness X",),
    )
    assert result.measurement_basis == basis


def test_verified_patch_artifact_id_recorded():
    patch = _real_patch()
    svc = CandidateVerificationService()

    result = svc.verify(
        run_id="r1",
        candidate_patch=patch,
        measurement_basis=("branch coverage",),
        observed_gains=("gain A",),
        residual_weaknesses=("weakness X",),
    )
    assert result.verified_patch_artifact_id == patch.artifact_id


# ---------------------------------------------------------------------------
# Non-authoritative posture
# ---------------------------------------------------------------------------


def test_verification_is_not_placeholder():
    patch = _real_patch()
    svc = CandidateVerificationService()

    result = svc.verify(
        run_id="r1",
        candidate_patch=patch,
        measurement_basis=("branch coverage",),
        observed_gains=("gain A",),
        residual_weaknesses=("weakness X",),
    )
    assert result.placeholder is False


def test_verification_authority_posture_is_non_authoritative():
    patch = _real_patch()
    svc = CandidateVerificationService()

    result = svc.verify(
        run_id="r1",
        candidate_patch=patch,
        measurement_basis=("branch coverage",),
        observed_gains=("gain A",),
        residual_weaknesses=("weakness X",),
    )
    assert result.authority_posture == ArtifactAuthorityPosture.NON_AUTHORITATIVE


def test_verification_artifact_family():
    patch = _real_patch()
    svc = CandidateVerificationService()

    result = svc.verify(
        run_id="r1",
        candidate_patch=patch,
        measurement_basis=("branch coverage",),
        observed_gains=("gain A",),
        residual_weaknesses=("weakness X",),
    )
    assert result.artifact_family == ArtifactFamily.CANDIDATE_VERIFICATION
