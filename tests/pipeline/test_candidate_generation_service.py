"""
Tests for CandidateGenerationService — forgeHQ Phase 3.

Covers design-before-generation enforcement, scope adherence (all modified refs
must be within context bundle), target_id consistency, and non-authoritative posture.
"""
import pytest

from app.domain.artifacts.enums import ArtifactAuthorityPosture, ArtifactFamily
from app.schemas.ranking_factor_trace import RankingFactor
from app.services.candidate_design_service import CandidateDesignService
from app.services.candidate_generation_service import (
    CandidateGenerationService,
    GenerationScopeError,
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
    oracle_strategy="Run test suite and measure new branch coverage",
    disconfirming_checks=("mutation survivors still present",),
    failure_hypotheses=("change breaks integration path",),
)


def _real_bundle(
    target_id: str = "service_a",
    run_id: str = "r1",
    context_item_refs: tuple[str, ...] = ("src/auth.py", "tests/test_auth.py"),
):
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
        context_item_refs=context_item_refs,
        scope_boundary_statement="bounded to auth module and its unit tests",
    )


def _real_design(bundle, run_id: str = "r1"):
    return CandidateDesignService().create_design(
        run_id=run_id, context_bundle=bundle, **_DESIGN_KWARGS
    )


# ---------------------------------------------------------------------------
# Fail-closed: placeholder design
# ---------------------------------------------------------------------------


def test_placeholder_design_raises_generation_scope_error():
    from app.schemas.candidate_design import CandidateDesign

    placeholder = CandidateDesign(run_id="r1")
    bundle = _real_bundle()
    svc = CandidateGenerationService()

    with pytest.raises(GenerationScopeError, match="placeholder design"):
        svc.generate_patch(
            run_id="r1",
            candidate_design=placeholder,
            context_bundle=bundle,
            modified_refs=("src/auth.py",),
        )


# ---------------------------------------------------------------------------
# Fail-closed: placeholder context bundle
# ---------------------------------------------------------------------------


def test_placeholder_bundle_raises_generation_scope_error():
    from app.schemas.context_bundle import ContextBundle

    bundle = _real_bundle()
    design = _real_design(bundle)
    placeholder_bundle = ContextBundle(run_id="r1")
    svc = CandidateGenerationService()

    with pytest.raises(GenerationScopeError, match="placeholder context bundle"):
        svc.generate_patch(
            run_id="r1",
            candidate_design=design,
            context_bundle=placeholder_bundle,
            modified_refs=(),
        )


# ---------------------------------------------------------------------------
# Fail-closed: target_id mismatch
# ---------------------------------------------------------------------------


def test_design_target_id_mismatch_raises_scope_error():
    bundle_a = _real_bundle(target_id="service_a")
    design_a = _real_design(bundle_a)
    bundle_b = _real_bundle(target_id="service_b")
    svc = CandidateGenerationService()

    with pytest.raises(GenerationScopeError, match="scope escape"):
        svc.generate_patch(
            run_id="r1",
            candidate_design=design_a,
            context_bundle=bundle_b,
            modified_refs=(),
        )


# ---------------------------------------------------------------------------
# Fail-closed: modified refs outside scope
# ---------------------------------------------------------------------------


def test_out_of_scope_modified_ref_raises_scope_error():
    bundle = _real_bundle(context_item_refs=("src/auth.py", "tests/test_auth.py"))
    design = _real_design(bundle)
    svc = CandidateGenerationService()

    with pytest.raises(GenerationScopeError, match="scope escape"):
        svc.generate_patch(
            run_id="r1",
            candidate_design=design,
            context_bundle=bundle,
            modified_refs=("src/auth.py", "src/OTHER_MODULE.py"),  # out of scope
        )


def test_empty_bundle_with_nonempty_modified_refs_raises_scope_error():
    bundle = _real_bundle(context_item_refs=())
    design = _real_design(bundle)
    svc = CandidateGenerationService()

    with pytest.raises(GenerationScopeError, match="zero admitted items"):
        svc.generate_patch(
            run_id="r1",
            candidate_design=design,
            context_bundle=bundle,
            modified_refs=("src/auth.py",),
        )


# ---------------------------------------------------------------------------
# Valid patch creation
# ---------------------------------------------------------------------------


def test_valid_patch_created_from_design():
    bundle = _real_bundle()
    design = _real_design(bundle)
    svc = CandidateGenerationService()

    patch = svc.generate_patch(
        run_id="r1",
        candidate_design=design,
        context_bundle=bundle,
        modified_refs=("src/auth.py",),
    )
    assert patch.design_artifact_id == design.artifact_id
    assert patch.modified_refs == ("src/auth.py",)
    assert patch.scope_adherence_verified is True


def test_empty_modified_refs_is_valid_for_nonempty_bundle():
    """Zero modifications within scope is a legitimate (empty) patch."""
    bundle = _real_bundle()
    design = _real_design(bundle)
    svc = CandidateGenerationService()

    patch = svc.generate_patch(
        run_id="r1",
        candidate_design=design,
        context_bundle=bundle,
        modified_refs=(),
    )
    assert patch.modified_refs == ()
    assert patch.scope_adherence_verified is True


def test_all_bundle_items_modifiable():
    bundle = _real_bundle(context_item_refs=("src/auth.py", "tests/test_auth.py"))
    design = _real_design(bundle)
    svc = CandidateGenerationService()

    patch = svc.generate_patch(
        run_id="r1",
        candidate_design=design,
        context_bundle=bundle,
        modified_refs=("src/auth.py", "tests/test_auth.py"),
    )
    assert set(patch.modified_refs) == {"src/auth.py", "tests/test_auth.py"}


def test_patch_parent_refs_point_to_design():
    bundle = _real_bundle()
    design = _real_design(bundle)
    svc = CandidateGenerationService()

    patch = svc.generate_patch(
        run_id="r1",
        candidate_design=design,
        context_bundle=bundle,
        modified_refs=("src/auth.py",),
    )
    assert design.artifact_id in patch.parent_artifact_ids


# ---------------------------------------------------------------------------
# Non-authoritative posture
# ---------------------------------------------------------------------------


def test_patch_is_not_placeholder():
    bundle = _real_bundle()
    design = _real_design(bundle)
    svc = CandidateGenerationService()

    patch = svc.generate_patch(
        run_id="r1",
        candidate_design=design,
        context_bundle=bundle,
        modified_refs=("src/auth.py",),
    )
    assert patch.placeholder is False


def test_patch_authority_posture_is_non_authoritative():
    bundle = _real_bundle()
    design = _real_design(bundle)
    svc = CandidateGenerationService()

    patch = svc.generate_patch(
        run_id="r1",
        candidate_design=design,
        context_bundle=bundle,
        modified_refs=(),
    )
    assert patch.authority_posture == ArtifactAuthorityPosture.NON_AUTHORITATIVE


def test_patch_artifact_family():
    bundle = _real_bundle()
    design = _real_design(bundle)
    svc = CandidateGenerationService()

    patch = svc.generate_patch(
        run_id="r1",
        candidate_design=design,
        context_bundle=bundle,
        modified_refs=(),
    )
    assert patch.artifact_family == ArtifactFamily.CANDIDATE_PATCH
