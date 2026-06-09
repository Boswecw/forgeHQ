"""
Tests for ContextCurationBridge — forgeHQ Stage 3 wired to context-runtime.

Covers: governed-handle integrity (fail-closed), provenance propagation into the
bundle's scope boundary, admitted-ref adoption, and that the underlying
ContextBundleService scope guards still apply.
"""
import pytest

from app.domain.artifacts.enums import ArtifactAuthorityPosture, ArtifactFamily
from app.schemas.ranking_factor_trace import RankingFactor
from app.services.context_bundle_service import ScopeEscapeError
from app.services.context_curation_bridge import ContextCurationBridge, ContextCurationError
from app.services.signal_intake_service import SignalIntakeService
from app.services.target_ranking_service import TargetRankingService


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


def _governed_result(
    bundle_id: str = "ctxb_eda10b46fc1d0dfc",
    bundle_hash: str = "eda10b46fc1d0dfc",
    refs=("file://forgehq/app/services/x.py", "doc://forgehq/SYSTEM.md"),
):
    return {
        "context_bundle_id": bundle_id,
        "bundle_hash": bundle_hash,
        "manifest": {"context_bundle_id": bundle_id, "bundle_hash": bundle_hash},
        "payload_refs": list(refs),
        "context_item_refs": list(refs),
    }


# --------------------------------------------------------------------------- #
# Happy path
# --------------------------------------------------------------------------- #


def test_curates_governed_bundle_with_admitted_refs():
    bridge = ContextCurationBridge()
    bundle = bridge.curate_from_runtime(
        run_id="r1",
        target_id="service_a",
        target_ranking=_real_ranking(),
        assemble_result=_governed_result(),
    )
    assert bundle.placeholder is False
    assert bundle.target_id == "service_a"
    assert bundle.authority_posture == ArtifactAuthorityPosture.NON_AUTHORITATIVE
    assert bundle.artifact_family == ArtifactFamily.CONTEXT_BUNDLE
    assert bundle.context_item_refs == (
        "file://forgehq/app/services/x.py",
        "doc://forgehq/SYSTEM.md",
    )


def test_governed_handle_is_carried_into_scope_boundary():
    bridge = ContextCurationBridge()
    bundle = bridge.curate_from_runtime(
        run_id="r1",
        target_id="service_a",
        target_ranking=_real_ranking(),
        assemble_result=_governed_result(),
    )
    # The PCC governed handle rides along in the (locked) scope statement so it
    # propagates through design/generation into the proposal.
    assert "ctxb_eda10b46fc1d0dfc" in bundle.scope_boundary_statement
    assert "eda10b46fc1d0dfc" in bundle.scope_boundary_statement
    assert "governed by context-runtime" in bundle.scope_boundary_statement


def test_custom_scope_statement_is_preserved_with_provenance_appended():
    bridge = ContextCurationBridge()
    bundle = bridge.curate_from_runtime(
        run_id="r1",
        target_id="service_a",
        target_ranking=_real_ranking(),
        assemble_result=_governed_result(),
        scope_boundary_statement="bounded to service_a only",
    )
    assert bundle.scope_boundary_statement.startswith("bounded to service_a only")
    assert "ctxb_eda10b46fc1d0dfc" in bundle.scope_boundary_statement


def test_accepts_payload_refs_when_context_item_refs_absent():
    bridge = ContextCurationBridge()
    result = _governed_result()
    del result["context_item_refs"]
    bundle = bridge.curate_from_runtime(
        run_id="r1",
        target_id="service_a",
        target_ranking=_real_ranking(),
        assemble_result=result,
    )
    assert len(bundle.context_item_refs) == 2


# --------------------------------------------------------------------------- #
# Fail-closed: governed-handle integrity
# --------------------------------------------------------------------------- #


def test_missing_bundle_id_fails_closed():
    bridge = ContextCurationBridge()
    result = _governed_result()
    del result["context_bundle_id"]
    with pytest.raises(ContextCurationError, match="context_bundle_id"):
        bridge.curate_from_runtime(
            run_id="r1",
            target_id="service_a",
            target_ranking=_real_ranking(),
            assemble_result=result,
        )


def test_non_ctxb_bundle_id_fails_closed():
    bridge = ContextCurationBridge()
    result = _governed_result(bundle_id="bundle-123")
    with pytest.raises(ContextCurationError, match="context_bundle_id"):
        bridge.curate_from_runtime(
            run_id="r1",
            target_id="service_a",
            target_ranking=_real_ranking(),
            assemble_result=result,
        )


def test_missing_bundle_hash_fails_closed():
    bridge = ContextCurationBridge()
    result = _governed_result()
    result["bundle_hash"] = "   "
    with pytest.raises(ContextCurationError, match="bundle_hash"):
        bridge.curate_from_runtime(
            run_id="r1",
            target_id="service_a",
            target_ranking=_real_ranking(),
            assemble_result=result,
        )


def test_missing_refs_fails_closed():
    bridge = ContextCurationBridge()
    result = _governed_result()
    del result["context_item_refs"]
    del result["payload_refs"]
    with pytest.raises(ContextCurationError, match="context_item_refs"):
        bridge.curate_from_runtime(
            run_id="r1",
            target_id="service_a",
            target_ranking=_real_ranking(),
            assemble_result=result,
        )


# --------------------------------------------------------------------------- #
# Fail-closed: underlying bounded-scope guards still apply
# --------------------------------------------------------------------------- #


def test_target_mismatch_still_fails_closed():
    bridge = ContextCurationBridge()
    with pytest.raises(ScopeEscapeError):
        bridge.curate_from_runtime(
            run_id="r1",
            target_id="service_b",  # ranking is for service_a
            target_ranking=_real_ranking(target_id="service_a"),
            assemble_result=_governed_result(),
        )


def test_placeholder_ranking_still_fails_closed():
    from app.schemas.target_ranking import TargetRanking

    bridge = ContextCurationBridge()
    with pytest.raises(ScopeEscapeError):
        bridge.curate_from_runtime(
            run_id="r1",
            target_id="service_a",
            target_ranking=TargetRanking(run_id="r1"),
            assemble_result=_governed_result(),
        )
