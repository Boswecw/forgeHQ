"""forgeHQ lineage emitter unit tests."""

from __future__ import annotations

import sys
from pathlib import Path

_FORGEHQ_ROOT = Path(__file__).resolve().parents[2]
if str(_FORGEHQ_ROOT) not in sys.path:
    sys.path.insert(0, str(_FORGEHQ_ROOT))

from tests.lineage._lineage_harness import make_recording_client  # noqa: E402

from app.lineage.emitter import ForgeHQLineageEmitter, NullLineageEmitter  # noqa: E402


def _emitter() -> tuple[ForgeHQLineageEmitter, object]:
    client, backend = make_recording_client(writer_identity="forgehq", writer_token="local-forgehq")
    return ForgeHQLineageEmitter(client), backend


def test_signal_intake_consumed_writes_node_and_consumed_by_edge():
    emitter, backend = _emitter()
    status = emitter.emit_signal_intake_consumed(
        signal_intake_id="intake-001",
        forgemath_output_node_id="node:forgemath_output:abcd",
        source_output_id="forgemath_output:abcd",
        source_payload_hash="c" * 64,
        ingested_at="2026-05-04T16:30:00Z",
    )
    assert status.outcome == "lineage_available"
    assert status.signal_intake_node_id and status.consumed_by_edge_id
    env = backend.envelopes[-1]
    assert env["nodes"][0]["node_type"] == "forgehq_signal_intake"
    assert env["edges"][0]["edge_type"] == "consumed_by"
    assert env["edges"][0]["causality_class"] == "deterministic"


def test_shaping_candidate_links_to_intake_via_informed_edge():
    emitter, backend = _emitter()
    intake = emitter.emit_signal_intake_consumed(
        signal_intake_id="intake-002",
        forgemath_output_node_id="node:forgemath_output:xx",
        source_output_id="forgemath_output:xx",
        ingested_at="2026-05-04T16:30:00Z",
    )
    cand = emitter.emit_shaping_candidate(
        candidate_id="cand-002",
        signal_intake_node_id=intake.signal_intake_node_id,
        proposed_at="2026-05-04T16:31:00Z",
        summary="lower target ranking on lane B",
    )
    assert cand.outcome == "lineage_available"
    last = backend.envelopes[-1]
    assert last["nodes"][0]["node_type"] == "forgehq_shaping_candidate"
    assert last["edges"][0]["edge_type"] == "informed"


def test_reviewability_result_emits_required_review_edge():
    emitter, backend = _emitter()
    intake = emitter.emit_signal_intake_consumed(
        signal_intake_id="intake-003",
        forgemath_output_node_id="node:forgemath_output:yy",
        source_output_id="forgemath_output:yy",
        ingested_at="2026-05-04T16:30:00Z",
    )
    cand = emitter.emit_shaping_candidate(
        candidate_id="cand-003",
        signal_intake_node_id=intake.signal_intake_node_id,
        proposed_at="2026-05-04T16:31:00Z",
    )
    result = emitter.emit_reviewability_result(
        reviewability_id="rev-003",
        candidate_node_id=cand.shaping_candidate_node_id,
        candidate_id="cand-003",
        state="REVIEWABLE",
        decided_at="2026-05-04T16:32:00Z",
        lineage_availability="lineage_available",
    )
    assert result.outcome == "lineage_available"
    last = backend.envelopes[-1]
    assert last["nodes"][0]["node_type"] == "forgehq_reviewability_result"
    assert last["edges"][0]["edge_type"] == "required_review"


def test_emitter_is_non_blocking_when_unreachable():
    from forge_lineage_sdk import LineageClient

    sdk = LineageClient(
        base_url="http://127.0.0.1:1",
        writer_identity="forgehq",
        writer_token="local-forgehq",
    )
    em = ForgeHQLineageEmitter(sdk)
    s = em.emit_signal_intake_consumed(
        signal_intake_id="x",
        forgemath_output_node_id="x",
        source_output_id="x",
        ingested_at="2026-05-04T00:00:00Z",
    )
    assert s.outcome in ("lineage_missing", "lineage_degraded")


def test_null_emitter_is_safe():
    n = NullLineageEmitter()
    assert n.emit_signal_intake_consumed(signal_intake_id="x").outcome == "lineage_missing"
    assert n.emit_shaping_candidate(candidate_id="x").outcome == "lineage_missing"
    assert n.emit_reviewability_result(reviewability_id="x").outcome == "lineage_missing"
