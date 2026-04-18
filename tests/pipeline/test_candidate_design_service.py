"""
Tests for CandidateDesignService — forgeHQ Phase 3.

Covers fail-closed behavior for placeholder bundles, empty required fields,
scope locking from context bundle, and non-authoritative posture.
"""
import pytest

from app.domain.artifacts.enums import ArtifactAuthorityPosture, ArtifactFamily
from app.schemas.ranking_factor_trace import RankingFactor
from app.services.candidate_design_service import CandidateDesignService, DesignError
from app.services.context_bundle_service import ContextBundleService
from app.services.signal_intake_service import SignalIntakeService
from app.services.target_ranking_service import TargetRankingService


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_DESIGN_KWARGS = dict(
    change_hypothesis="Add branch coverage for the null path in auth handler",
    intended_confidence_gain="Raise branch coverage from 62% to 80% on auth module",
    targeted_behaviors=("null input returns 401", "expired token returns 403"),
    oracle_strategy="Run existing test suite; assert new branch lines are covered",
    disconfirming_checks=("mutation survivors still present after change",),
    failure_hypotheses=("change breaks unrelated integration path",),
)


def _real_bundle(target_id: str = "service_a", run_id: str = "r1"):
    snapshot = SignalIntakeService().admit_signals(
        run_id=run_id, source_refs=("forgeeval://coverage/auth",)
    )[0]
    factor = RankingFactor(
        factor_name="coverage_gap",
        raw_value=0.6,
        normalized_score=0.6,
        source_ref="forgeeval://coverage/auth",
        is_deterministic=True,
        explanation="auth coverage gap",
    )
    ranking, _ = TargetRankingService().rank_target(
        run_id=run_id,
        target_id=target_id,
        signal_snapshot=snapshot,
        ranking_factors=(factor,),
    )
    return ContextBundleService().build_context_bundle(
        run_id=run_id,
        target_id=target_id,
        target_ranking=ranking,
        context_item_refs=("src/auth.py", "tests/test_auth.py"),
        scope_boundary_statement="bounded to auth module and its unit tests",
    )


# ---------------------------------------------------------------------------
# Fail-closed: placeholder context bundle
# ---------------------------------------------------------------------------


def test_placeholder_bundle_raises_design_error():
    from app.schemas.context_bundle import ContextBundle

    bundle = ContextBundle(run_id="r1")
    svc = CandidateDesignService()

    with pytest.raises(DesignError, match="placeholder"):
        svc.create_design(run_id="r1", context_bundle=bundle, **_DESIGN_KWARGS)


# ---------------------------------------------------------------------------
# Fail-closed: empty required fields
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "field_name,override",
    [
        ("change_hypothesis", dict(change_hypothesis="")),
        ("change_hypothesis", dict(change_hypothesis="   ")),
        ("intended_confidence_gain", dict(intended_confidence_gain="")),
        ("oracle_strategy", dict(oracle_strategy="")),
        ("targeted_behaviors", dict(targeted_behaviors=())),
        ("disconfirming_checks", dict(disconfirming_checks=())),
        ("failure_hypotheses", dict(failure_hypotheses=())),
    ],
)
def test_empty_required_field_raises_design_error(field_name, override):
    bundle = _real_bundle()
    svc = CandidateDesignService()
    kwargs = {**_DESIGN_KWARGS, **override}

    with pytest.raises(DesignError):
        svc.create_design(run_id="r1", context_bundle=bundle, **kwargs)


# ---------------------------------------------------------------------------
# Scope locking from context bundle
# ---------------------------------------------------------------------------


def test_design_target_id_matches_context_bundle():
    bundle = _real_bundle(target_id="service_a")
    svc = CandidateDesignService()
    design = svc.create_design(run_id="r1", context_bundle=bundle, **_DESIGN_KWARGS)
    assert design.target_id == "service_a"


def test_design_scope_boundary_locked_from_bundle():
    bundle = _real_bundle()
    svc = CandidateDesignService()
    design = svc.create_design(run_id="r1", context_bundle=bundle, **_DESIGN_KWARGS)
    assert design.scope_boundary_statement == bundle.scope_boundary_statement


def test_design_context_bundle_artifact_id_preserved():
    bundle = _real_bundle()
    svc = CandidateDesignService()
    design = svc.create_design(run_id="r1", context_bundle=bundle, **_DESIGN_KWARGS)
    assert design.context_bundle_artifact_id == bundle.artifact_id


def test_design_parent_refs_point_to_bundle():
    bundle = _real_bundle()
    svc = CandidateDesignService()
    design = svc.create_design(run_id="r1", context_bundle=bundle, **_DESIGN_KWARGS)
    assert bundle.artifact_id in design.parent_artifact_ids


# ---------------------------------------------------------------------------
# Valid design creation
# ---------------------------------------------------------------------------


def test_valid_design_created():
    bundle = _real_bundle()
    svc = CandidateDesignService()
    design = svc.create_design(run_id="r1", context_bundle=bundle, **_DESIGN_KWARGS)

    assert design.change_hypothesis == _DESIGN_KWARGS["change_hypothesis"]
    assert design.intended_confidence_gain == _DESIGN_KWARGS["intended_confidence_gain"]
    assert design.oracle_strategy == _DESIGN_KWARGS["oracle_strategy"]
    assert design.targeted_behaviors == _DESIGN_KWARGS["targeted_behaviors"]
    assert design.disconfirming_checks == _DESIGN_KWARGS["disconfirming_checks"]
    assert design.failure_hypotheses == _DESIGN_KWARGS["failure_hypotheses"]


# ---------------------------------------------------------------------------
# Non-authoritative posture
# ---------------------------------------------------------------------------


def test_design_is_not_placeholder():
    bundle = _real_bundle()
    svc = CandidateDesignService()
    design = svc.create_design(run_id="r1", context_bundle=bundle, **_DESIGN_KWARGS)
    assert design.placeholder is False


def test_design_authority_posture_is_non_authoritative():
    bundle = _real_bundle()
    svc = CandidateDesignService()
    design = svc.create_design(run_id="r1", context_bundle=bundle, **_DESIGN_KWARGS)
    assert design.authority_posture == ArtifactAuthorityPosture.NON_AUTHORITATIVE


def test_design_artifact_family():
    bundle = _real_bundle()
    svc = CandidateDesignService()
    design = svc.create_design(run_id="r1", context_bundle=bundle, **_DESIGN_KWARGS)
    assert design.artifact_family == ArtifactFamily.CANDIDATE_DESIGN
