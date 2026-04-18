"""
Tests for TargetRankingService — forgeHQ Phase 2.

Covers fail-closed behavior for placeholder snapshots and missing factors,
source-ref validation, composite score computation, deterministic factor
weighting, and non-authoritative posture requirements.
"""
import pytest

from app.domain.artifacts.enums import ArtifactAuthorityPosture, ArtifactFamily
from app.schemas.ranking_factor_trace import RankingFactor
from app.services.signal_intake_service import SignalIntakeService
from app.services.target_ranking_service import RankingError, TargetRankingService


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _admitted_snapshot(run_id: str = "r1"):
    return SignalIntakeService().admit_signals(
        run_id=run_id,
        source_refs=(
            "forgeeval://coverage/module_a",
            "signal://mutation/suite_b",
        ),
    )[0]


def _factor(
    *,
    name: str = "coverage_gap",
    raw_value: float = 0.5,
    normalized_score: float = 0.5,
    source_ref: str = "forgeeval://coverage/module_a",
    is_deterministic: bool = True,
    explanation: str = "test factor",
) -> RankingFactor:
    return RankingFactor(
        factor_name=name,
        raw_value=raw_value,
        normalized_score=normalized_score,
        source_ref=source_ref,
        is_deterministic=is_deterministic,
        explanation=explanation,
    )


# ---------------------------------------------------------------------------
# Fail-closed: placeholder snapshot
# ---------------------------------------------------------------------------


def test_placeholder_snapshot_raises_ranking_error():
    from app.schemas.signal_snapshot import SignalSnapshot

    placeholder = SignalSnapshot(run_id="r1")
    svc = TargetRankingService()

    with pytest.raises(RankingError, match="placeholder"):
        svc.rank_target(
            run_id="r1",
            target_id="service_a",
            signal_snapshot=placeholder,
            ranking_factors=(_factor(),),
        )


# ---------------------------------------------------------------------------
# Fail-closed: no ranking factors
# ---------------------------------------------------------------------------


def test_empty_ranking_factors_raises_ranking_error():
    snapshot = _admitted_snapshot()
    svc = TargetRankingService()

    with pytest.raises(RankingError, match="factor"):
        svc.rank_target(
            run_id="r1",
            target_id="service_a",
            signal_snapshot=snapshot,
            ranking_factors=(),
        )


# ---------------------------------------------------------------------------
# Fail-closed: factor source ref not in admitted snapshot
# ---------------------------------------------------------------------------


def test_factor_with_unadmitted_source_ref_raises_ranking_error():
    snapshot = _admitted_snapshot()
    svc = TargetRankingService()

    bad_factor = _factor(source_ref="forgeeval://not_in_snapshot/x")

    with pytest.raises(RankingError, match="not in the admitted signal snapshot"):
        svc.rank_target(
            run_id="r1",
            target_id="service_a",
            signal_snapshot=snapshot,
            ranking_factors=(bad_factor,),
        )


# ---------------------------------------------------------------------------
# Composite score computation
# ---------------------------------------------------------------------------


def test_single_factor_score_equals_normalized_score():
    snapshot = _admitted_snapshot()
    svc = TargetRankingService()

    ranking, _ = svc.rank_target(
        run_id="r1",
        target_id="service_a",
        signal_snapshot=snapshot,
        ranking_factors=(_factor(normalized_score=0.7),),
    )
    assert abs(ranking.composite_score - 0.7) < 1e-9


def test_deterministic_factors_receive_double_weight():
    snapshot = _admitted_snapshot()
    svc = TargetRankingService()

    deterministic = _factor(
        name="det",
        normalized_score=1.0,
        source_ref="forgeeval://coverage/module_a",
        is_deterministic=True,
    )
    weak = _factor(
        name="weak",
        normalized_score=0.0,
        source_ref="signal://mutation/suite_b",
        is_deterministic=False,
    )

    ranking, _ = svc.rank_target(
        run_id="r1",
        target_id="service_a",
        signal_snapshot=snapshot,
        ranking_factors=(deterministic, weak),
    )
    # weight_det=2, weight_weak=1 → (1.0*2 + 0.0*1) / 3 = 0.666...
    assert abs(ranking.composite_score - 2.0 / 3.0) < 1e-9


def test_two_equal_weak_factors_average_to_their_score():
    snapshot = _admitted_snapshot()
    svc = TargetRankingService()

    f1 = _factor(
        name="f1",
        normalized_score=0.4,
        source_ref="signal://mutation/suite_b",
        is_deterministic=False,
    )
    f2 = _factor(
        name="f2",
        normalized_score=0.6,
        source_ref="signal://mutation/suite_b",
        is_deterministic=False,
    )

    ranking, _ = svc.rank_target(
        run_id="r1",
        target_id="service_a",
        signal_snapshot=snapshot,
        ranking_factors=(f1, f2),
    )
    assert abs(ranking.composite_score - 0.5) < 1e-9


# ---------------------------------------------------------------------------
# Ranking trace explainability
# ---------------------------------------------------------------------------


def test_ranking_trace_contains_all_factors():
    snapshot = _admitted_snapshot()
    svc = TargetRankingService()
    f1 = _factor(name="f1")
    f2 = _factor(name="f2", source_ref="signal://mutation/suite_b", is_deterministic=False)

    _, trace = svc.rank_target(
        run_id="r1",
        target_id="service_a",
        signal_snapshot=snapshot,
        ranking_factors=(f1, f2),
    )
    factor_names = {f.factor_name for f in trace.factors}
    assert "f1" in factor_names
    assert "f2" in factor_names


def test_ranking_trace_composite_score_matches_ranking():
    snapshot = _admitted_snapshot()
    svc = TargetRankingService()

    ranking, trace = svc.rank_target(
        run_id="r1",
        target_id="service_a",
        signal_snapshot=snapshot,
        ranking_factors=(_factor(normalized_score=0.8),),
    )
    assert ranking.composite_score == trace.composite_score


def test_ranking_artifact_id_stored_in_ranking():
    snapshot = _admitted_snapshot()
    svc = TargetRankingService()

    ranking, trace = svc.rank_target(
        run_id="r1",
        target_id="service_a",
        signal_snapshot=snapshot,
        ranking_factors=(_factor(),),
    )
    assert ranking.ranking_trace_artifact_id == trace.artifact_id


# ---------------------------------------------------------------------------
# Non-authoritative posture
# ---------------------------------------------------------------------------


def test_ranking_is_not_placeholder():
    snapshot = _admitted_snapshot()
    svc = TargetRankingService()
    ranking, _ = svc.rank_target(
        run_id="r1",
        target_id="service_a",
        signal_snapshot=snapshot,
        ranking_factors=(_factor(),),
    )
    assert ranking.placeholder is False


def test_ranking_authority_posture_is_non_authoritative():
    snapshot = _admitted_snapshot()
    svc = TargetRankingService()
    ranking, _ = svc.rank_target(
        run_id="r1",
        target_id="service_a",
        signal_snapshot=snapshot,
        ranking_factors=(_factor(),),
    )
    assert ranking.authority_posture == ArtifactAuthorityPosture.NON_AUTHORITATIVE


def test_ranking_artifact_family():
    snapshot = _admitted_snapshot()
    svc = TargetRankingService()
    ranking, _ = svc.rank_target(
        run_id="r1",
        target_id="service_a",
        signal_snapshot=snapshot,
        ranking_factors=(_factor(),),
    )
    assert ranking.artifact_family == ArtifactFamily.TARGET_RANKING
