"""
Tests for FalsificationService — forgeHQ Phase 4 (Critic lane).

Covers: fail-closed on placeholders and missing evaluated checks,
contradiction/duplicate/shallow-gain downgrade logic, critic lane
independence, and non-authoritative posture.
"""
import pytest

from app.domain.artifacts.enums import ArtifactAuthorityPosture, ArtifactFamily
from app.domain.reviewability.enums import ChallengePosture
from app.schemas.ranking_factor_trace import RankingFactor
from app.services.candidate_design_service import CandidateDesignService
from app.services.candidate_generation_service import CandidateGenerationService
from app.services.context_bundle_service import ContextBundleService
from app.services.falsification_service import FalsificationError, FalsificationService
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
    disconfirming_checks=("mutation survivors still present", "integration path intact"),
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
    ), design


# ---------------------------------------------------------------------------
# Fail-closed: placeholder patch
# ---------------------------------------------------------------------------


def test_placeholder_patch_raises_falsification_error():
    from app.schemas.candidate_patch import CandidatePatch
    from app.schemas.candidate_design import CandidateDesign

    svc = FalsificationService()
    with pytest.raises(FalsificationError, match="placeholder patch"):
        svc.challenge(
            run_id="r1",
            candidate_patch=CandidatePatch(run_id="r1"),
            candidate_design=CandidateDesign(run_id="r1"),
            disconfirming_checks_evaluated=("check-1",),
        )


# ---------------------------------------------------------------------------
# Fail-closed: placeholder design
# ---------------------------------------------------------------------------


def test_placeholder_design_raises_falsification_error():
    from app.schemas.candidate_design import CandidateDesign

    patch, _ = _real_patch()
    svc = FalsificationService()

    with pytest.raises(FalsificationError, match="placeholder design"):
        svc.challenge(
            run_id="r1",
            candidate_patch=patch,
            candidate_design=CandidateDesign(run_id="r1"),
            disconfirming_checks_evaluated=("check-1",),
        )


# ---------------------------------------------------------------------------
# Fail-closed: no evaluated checks
# ---------------------------------------------------------------------------


def test_empty_evaluated_checks_raises_falsification_error():
    patch, design = _real_patch()
    svc = FalsificationService()

    with pytest.raises(FalsificationError, match="disconfirming check"):
        svc.challenge(
            run_id="r1",
            candidate_patch=patch,
            candidate_design=design,
            disconfirming_checks_evaluated=(),
        )


# ---------------------------------------------------------------------------
# Challenge posture — PASSED
# ---------------------------------------------------------------------------


def test_no_issues_yields_passed_posture():
    patch, design = _real_patch()
    svc = FalsificationService()

    report = svc.challenge(
        run_id="r1",
        candidate_patch=patch,
        candidate_design=design,
        disconfirming_checks_evaluated=("mutation survivors still present",),
    )
    assert report.challenge_posture == ChallengePosture.PASSED
    assert report.downgrade_applied is False
    assert report.downgrade_reasons == ()


# ---------------------------------------------------------------------------
# Downgrade logic
# ---------------------------------------------------------------------------


def test_contradiction_triggers_downgrade():
    patch, design = _real_patch()
    svc = FalsificationService()

    report = svc.challenge(
        run_id="r1",
        candidate_patch=patch,
        candidate_design=design,
        disconfirming_checks_evaluated=("mutation survivors still present",),
        contradictions=("patch modifies unrelated code path",),
    )
    assert report.challenge_posture == ChallengePosture.DOWNGRADED
    assert report.downgrade_applied is True
    assert len(report.downgrade_reasons) >= 1


def test_duplicate_test_warning_triggers_downgrade():
    patch, design = _real_patch()
    svc = FalsificationService()

    report = svc.challenge(
        run_id="r1",
        candidate_patch=patch,
        candidate_design=design,
        disconfirming_checks_evaluated=("check-1",),
        duplicate_test_warnings=("test_null_path already exists in test_auth.py",),
    )
    assert report.challenge_posture == ChallengePosture.DOWNGRADED
    assert report.downgrade_applied is True


def test_shallow_gain_indicator_triggers_downgrade():
    patch, design = _real_patch()
    svc = FalsificationService()

    report = svc.challenge(
        run_id="r1",
        candidate_patch=patch,
        candidate_design=design,
        disconfirming_checks_evaluated=("check-1",),
        shallow_gain_indicators=("branch count increase is 1 line only",),
    )
    assert report.challenge_posture == ChallengePosture.DOWNGRADED
    assert report.downgrade_applied is True


def test_multiple_issues_all_recorded_in_downgrade_reasons():
    patch, design = _real_patch()
    svc = FalsificationService()

    report = svc.challenge(
        run_id="r1",
        candidate_patch=patch,
        candidate_design=design,
        disconfirming_checks_evaluated=("check-1",),
        contradictions=("contradiction A",),
        duplicate_test_warnings=("duplicate B",),
        shallow_gain_indicators=("shallow C",),
    )
    assert len(report.downgrade_reasons) == 3
    assert all("contradiction" in r or "duplicate" in r or "shallow" in r for r in report.downgrade_reasons)


# ---------------------------------------------------------------------------
# Residual concerns always present
# ---------------------------------------------------------------------------


def test_passed_report_has_default_residual_concern():
    patch, design = _real_patch()
    svc = FalsificationService()

    report = svc.challenge(
        run_id="r1",
        candidate_patch=patch,
        candidate_design=design,
        disconfirming_checks_evaluated=("check-1",),
    )
    assert len(report.residual_concerns) >= 1


def test_downgraded_report_residual_concerns_contain_issues():
    patch, design = _real_patch()
    svc = FalsificationService()

    report = svc.challenge(
        run_id="r1",
        candidate_patch=patch,
        candidate_design=design,
        disconfirming_checks_evaluated=("check-1",),
        contradictions=("contradiction A",),
    )
    assert any("contradiction" in c for c in report.residual_concerns)


# ---------------------------------------------------------------------------
# Structural independence (Critic lane must not share Generator state)
# ---------------------------------------------------------------------------


def test_challenged_patch_id_recorded():
    patch, design = _real_patch()
    svc = FalsificationService()

    report = svc.challenge(
        run_id="r1",
        candidate_patch=patch,
        candidate_design=design,
        disconfirming_checks_evaluated=("check-1",),
    )
    assert report.challenged_patch_artifact_id == patch.artifact_id


def test_evaluated_checks_preserved_in_report():
    patch, design = _real_patch()
    svc = FalsificationService()

    report = svc.challenge(
        run_id="r1",
        candidate_patch=patch,
        candidate_design=design,
        disconfirming_checks_evaluated=(
            "mutation survivors still present",
            "integration path intact",
        ),
    )
    assert "mutation survivors still present" in report.disconfirming_checks_evaluated
    assert "integration path intact" in report.disconfirming_checks_evaluated


# ---------------------------------------------------------------------------
# Non-authoritative posture
# ---------------------------------------------------------------------------


def test_report_is_not_placeholder():
    patch, design = _real_patch()
    svc = FalsificationService()

    report = svc.challenge(
        run_id="r1",
        candidate_patch=patch,
        candidate_design=design,
        disconfirming_checks_evaluated=("check-1",),
    )
    assert report.placeholder is False


def test_report_authority_posture_is_non_authoritative():
    patch, design = _real_patch()
    svc = FalsificationService()

    report = svc.challenge(
        run_id="r1",
        candidate_patch=patch,
        candidate_design=design,
        disconfirming_checks_evaluated=("check-1",),
    )
    assert report.authority_posture == ArtifactAuthorityPosture.NON_AUTHORITATIVE


def test_report_artifact_family():
    patch, design = _real_patch()
    svc = FalsificationService()

    report = svc.challenge(
        run_id="r1",
        candidate_patch=patch,
        candidate_design=design,
        disconfirming_checks_evaluated=("check-1",),
    )
    assert report.artifact_family == ArtifactFamily.FALSIFICATION_REPORT
