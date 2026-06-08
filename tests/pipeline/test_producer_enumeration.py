"""Tests for producer_enumeration — lineage/cloud records -> feeder inputs.

Covers node-type classification, non-eval skipping, cloud record mapping, and the
end-to-end enumeration -> feeder -> intake chain: lineage nodes (as the
DataForge-Local list surface returns them) become admitted signals.
"""
from app.services.eval_source_feeder import EvalSourceFeeder
from app.services.producer_enumeration import (
    cloud_proposals_from_records,
    cloud_record_to_proposal,
    eval_outputs_from_lineage,
    lineage_node_to_eval_output,
)
from app.services.signal_intake_service import SignalIntakeService


# ---------------------------------------------------------------------------
# lineage node -> EvalOutput
# ---------------------------------------------------------------------------


def test_forge_eval_node_maps_to_forgeeval_output():
    out = lineage_node_to_eval_output(
        {"node_type": "forge_eval_evidence_bundle", "node_id": "eb-1"}
    )
    assert out is not None
    assert out.to_source_ref() == "forgeeval://forge_eval_evidence_bundle/eb-1"


def test_forgemath_node_maps_to_forgemath_output():
    out = lineage_node_to_eval_output(
        {"node_type": "forgemath_evaluation", "node_id": "ev-1"}
    )
    assert out is not None
    assert out.to_source_ref() == "forgemath://forgemath_evaluation/ev-1"


def test_non_eval_node_is_skipped():
    assert lineage_node_to_eval_output(
        {"node_type": "forgehq_signal_intake", "node_id": "s-1"}
    ) is None


def test_node_missing_fields_is_skipped():
    assert lineage_node_to_eval_output({"node_type": "forge_eval_run"}) is None
    assert lineage_node_to_eval_output({"node_id": "x"}) is None


def test_eval_outputs_from_lineage_filters_and_maps_batch():
    nodes = [
        {"node_type": "forge_eval_run", "node_id": "run-1"},
        {"node_type": "forgehq_signal_intake", "node_id": "skip-me"},  # not eval
        {"node_type": "forgemath_output", "node_id": "out-1"},
    ]
    outputs = eval_outputs_from_lineage(nodes)
    assert tuple(o.to_source_ref() for o in outputs) == (
        "forgeeval://forge_eval_run/run-1",
        "forgemath://forgemath_output/out-1",
    )


# ---------------------------------------------------------------------------
# cloud record -> CloudProposal
# ---------------------------------------------------------------------------


def test_cloud_record_maps_to_proposal():
    p = cloud_record_to_proposal({"proposal_id": "p-1", "service": "neuroforge"})
    assert p is not None
    assert p.to_source_ref() == "cloud://neuroforge/p-1"


def test_cloud_record_without_id_is_skipped():
    assert cloud_record_to_proposal({"service": "neuroforge"}) is None


def test_cloud_proposals_from_records_skips_idless():
    proposals = cloud_proposals_from_records(
        [{"proposal_id": "p-1"}, {"service": "x"}, {"proposal_id": "p-2", "service": "y"}]
    )
    assert tuple(p.proposal_id for p in proposals) == ("p-1", "p-2")


# ---------------------------------------------------------------------------
# end-to-end: enumeration -> feeder -> intake
# ---------------------------------------------------------------------------


def test_enumerated_lineage_nodes_are_admitted_by_intake():
    # what the DataForge-Local list surface would return
    nodes = [
        {"node_type": "forge_eval_evidence_bundle", "node_id": "eb-1"},
        {"node_type": "forgemath_evaluation", "node_id": "ev-1"},
        {"node_type": "forgehq_reviewability_result", "node_id": "skip"},  # not eval
    ]
    outputs = eval_outputs_from_lineage(nodes)
    refs = EvalSourceFeeder().collect_source_refs(outputs)
    snapshot, diagnostics = SignalIntakeService().admit_signals("run-enum", refs)

    assert diagnostics.admitted_count == 2
    assert diagnostics.rejected_count == 0
    assert set(snapshot.admitted_source_refs) == {
        "forgeeval://forge_eval_evidence_bundle/eb-1",
        "forgemath://forgemath_evaluation/ev-1",
    }
