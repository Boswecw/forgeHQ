"""
Tests for ContextBundleService — forgeHQ Phase 2.

Covers fail-closed scope policy, target_id consistency, placeholder rejection,
duplicate ref rejection, and non-authoritative posture requirements.
"""
import pytest

from app.domain.artifacts.enums import ArtifactAuthorityPosture, ArtifactFamily
from app.schemas.ranking_factor_trace import RankingFactor
from app.services.context_bundle_service import SCOPE_MAX_ITEMS, ContextBundleService, ScopeEscapeError
from app.services.signal_intake_service import SignalIntakeService
from app.services.target_ranking_service import TargetRankingService


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _real_ranking(target_id: str = "service_a", run_id: str = "r1"):
    snapshot = SignalIntakeService().admit_signals(
        run_id=run_id,
        source_refs=("forgeeval://coverage/module_a",),
    )[0]
    factor = RankingFactor(
        factor_name="coverage_gap",
        raw_value=0.6,
        normalized_score=0.6,
        source_ref="forgeeval://coverage/module_a",
        is_deterministic=True,
        explanation="coverage gap metric",
    )
    ranking, _ = TargetRankingService().rank_target(
        run_id=run_id,
        target_id=target_id,
        signal_snapshot=snapshot,
        ranking_factors=(factor,),
    )
    return ranking


# ---------------------------------------------------------------------------
# Fail-closed: placeholder ranking
# ---------------------------------------------------------------------------


def test_placeholder_ranking_raises_scope_escape_error():
    from app.schemas.target_ranking import TargetRanking

    placeholder = TargetRanking(run_id="r1")
    svc = ContextBundleService()

    with pytest.raises(ScopeEscapeError, match="placeholder"):
        svc.build_context_bundle(
            run_id="r1",
            target_id="service_a",
            target_ranking=placeholder,
            context_item_refs=("file://src/mod_a.py",),
            scope_boundary_statement="bounded to module_a only",
        )


# ---------------------------------------------------------------------------
# Fail-closed: target_id mismatch
# ---------------------------------------------------------------------------


def test_target_id_mismatch_raises_scope_escape_error():
    ranking = _real_ranking(target_id="service_a")
    svc = ContextBundleService()

    with pytest.raises(ScopeEscapeError, match="scope escape"):
        svc.build_context_bundle(
            run_id="r1",
            target_id="service_b",  # different from ranking
            target_ranking=ranking,
            context_item_refs=("file://src/mod_a.py",),
            scope_boundary_statement="bounded to module_a only",
        )


# ---------------------------------------------------------------------------
# Fail-closed: empty scope boundary statement
# ---------------------------------------------------------------------------


def test_empty_scope_boundary_raises_scope_escape_error():
    ranking = _real_ranking()
    svc = ContextBundleService()

    with pytest.raises(ScopeEscapeError, match="scope_boundary_statement"):
        svc.build_context_bundle(
            run_id="r1",
            target_id="service_a",
            target_ranking=ranking,
            context_item_refs=("file://src/mod_a.py",),
            scope_boundary_statement="",
        )


def test_whitespace_only_scope_boundary_raises_scope_escape_error():
    ranking = _real_ranking()
    svc = ContextBundleService()

    with pytest.raises(ScopeEscapeError):
        svc.build_context_bundle(
            run_id="r1",
            target_id="service_a",
            target_ranking=ranking,
            context_item_refs=("file://src/mod_a.py",),
            scope_boundary_statement="   ",
        )


# ---------------------------------------------------------------------------
# Fail-closed: scope exceeds max items
# ---------------------------------------------------------------------------


def test_scope_exceeding_max_items_raises_scope_escape_error():
    ranking = _real_ranking()
    svc = ContextBundleService()
    too_many = tuple(f"file://src/mod_{i}.py" for i in range(SCOPE_MAX_ITEMS + 1))

    with pytest.raises(ScopeEscapeError, match="exceed"):
        svc.build_context_bundle(
            run_id="r1",
            target_id="service_a",
            target_ranking=ranking,
            context_item_refs=too_many,
            scope_boundary_statement="bounded to module_a",
        )


def test_exactly_max_items_is_accepted():
    ranking = _real_ranking()
    svc = ContextBundleService()
    exactly_max = tuple(f"file://src/mod_{i}.py" for i in range(SCOPE_MAX_ITEMS))

    bundle = svc.build_context_bundle(
        run_id="r1",
        target_id="service_a",
        target_ranking=ranking,
        context_item_refs=exactly_max,
        scope_boundary_statement="bounded to module_a",
    )
    assert len(bundle.context_item_refs) == SCOPE_MAX_ITEMS


# ---------------------------------------------------------------------------
# Fail-closed: duplicate refs
# ---------------------------------------------------------------------------


def test_duplicate_context_refs_raise_scope_escape_error():
    ranking = _real_ranking()
    svc = ContextBundleService()

    with pytest.raises(ScopeEscapeError, match="duplicate"):
        svc.build_context_bundle(
            run_id="r1",
            target_id="service_a",
            target_ranking=ranking,
            context_item_refs=("file://src/a.py", "file://src/a.py"),
            scope_boundary_statement="bounded to module_a",
        )


# ---------------------------------------------------------------------------
# Valid bundle creation
# ---------------------------------------------------------------------------


def test_valid_context_bundle_created():
    ranking = _real_ranking()
    svc = ContextBundleService()

    bundle = svc.build_context_bundle(
        run_id="r1",
        target_id="service_a",
        target_ranking=ranking,
        context_item_refs=("file://src/mod_a.py", "file://tests/test_mod_a.py"),
        scope_boundary_statement="bounded to service_a module and its direct tests",
    )
    assert bundle.target_id == "service_a"
    assert len(bundle.context_item_refs) == 2
    assert bundle.scope_class == "bounded_single_target"


def test_context_bundle_preserves_scope_boundary_statement():
    ranking = _real_ranking()
    svc = ContextBundleService()
    stmt = "bounded to service_a auth module only"

    bundle = svc.build_context_bundle(
        run_id="r1",
        target_id="service_a",
        target_ranking=ranking,
        context_item_refs=("file://src/auth.py",),
        scope_boundary_statement=stmt,
    )
    assert bundle.scope_boundary_statement == stmt


def test_empty_context_item_refs_is_valid():
    """Zero context items is technically allowed — no scope escape."""
    ranking = _real_ranking()
    svc = ContextBundleService()

    bundle = svc.build_context_bundle(
        run_id="r1",
        target_id="service_a",
        target_ranking=ranking,
        context_item_refs=(),
        scope_boundary_statement="no context items — bounded empty scope",
    )
    assert bundle.context_item_refs == ()


# ---------------------------------------------------------------------------
# Non-authoritative posture
# ---------------------------------------------------------------------------


def test_bundle_is_not_placeholder():
    ranking = _real_ranking()
    svc = ContextBundleService()

    bundle = svc.build_context_bundle(
        run_id="r1",
        target_id="service_a",
        target_ranking=ranking,
        context_item_refs=(),
        scope_boundary_statement="bounded empty scope",
    )
    assert bundle.placeholder is False


def test_bundle_authority_posture_is_non_authoritative():
    ranking = _real_ranking()
    svc = ContextBundleService()

    bundle = svc.build_context_bundle(
        run_id="r1",
        target_id="service_a",
        target_ranking=ranking,
        context_item_refs=(),
        scope_boundary_statement="bounded empty scope",
    )
    assert bundle.authority_posture == ArtifactAuthorityPosture.NON_AUTHORITATIVE


def test_bundle_artifact_family():
    ranking = _real_ranking()
    svc = ContextBundleService()

    bundle = svc.build_context_bundle(
        run_id="r1",
        target_id="service_a",
        target_ranking=ranking,
        context_item_refs=(),
        scope_boundary_statement="bounded empty scope",
    )
    assert bundle.artifact_family == ArtifactFamily.CONTEXT_BUNDLE


# ---------------------------------------------------------------------------
# Custom max_items override
# ---------------------------------------------------------------------------


def test_custom_max_items_enforced():
    ranking = _real_ranking()
    svc = ContextBundleService(max_items=3)

    with pytest.raises(ScopeEscapeError):
        svc.build_context_bundle(
            run_id="r1",
            target_id="service_a",
            target_ranking=ranking,
            context_item_refs=("a", "b", "c", "d"),
            scope_boundary_statement="bounded scope",
        )
