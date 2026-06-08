"""Tests for ForgeHQFeedDriver — enumerate -> feed -> real-intake run.

The driver ties P1 (feeders) + P2 (enumeration) + P3 (real intake): producer
records (lineage nodes + cloud proposals) drive a shaping run whose SIGNAL_INTAKE
is real, completing to a ForgeHQProposal.
"""
import pytest

from app.domain.artifacts.enums import ArtifactFamily
from app.domain.pipeline.enums import PIPELINE_STAGE_ORDER
from app.orchestration.forgehq_feed_driver import ForgeHQFeedDriver
from app.services.signal_intake_service import NoAdmittedSourcesError


_LINEAGE = [
    {"node_type": "forge_eval_evidence_bundle", "node_id": "eb-1"},
    {"node_type": "forgemath_evaluation", "node_id": "ev-1"},
    {"node_type": "forgehq_signal_intake", "node_id": "skip"},  # not eval -> skipped
]
_CLOUD = [{"proposal_id": "p-1", "service": "neuroforge"}]


def test_collect_source_refs_enumerates_and_feeds():
    refs = ForgeHQFeedDriver().collect_source_refs(
        lineage_nodes=_LINEAGE, cloud_records=_CLOUD
    )
    assert refs == (
        "forgeeval://forge_eval_evidence_bundle/eb-1",
        "forgemath://forgemath_evaluation/ev-1",
        "cloud://neuroforge/p-1",
    )


def test_driver_runs_fed_pipeline_end_to_end():
    run = ForgeHQFeedDriver().run(
        "fed-run", lineage_nodes=_LINEAGE, cloud_records=_CLOUD
    )
    assert run.completed_stages == PIPELINE_STAGE_ORDER
    assert run.has_artifact(ArtifactFamily.FORGEHQ_PROPOSAL)

    snap = run.get_artifact(ArtifactFamily.SIGNAL_SNAPSHOT)
    assert snap.placeholder is False
    assert set(snap.admitted_source_refs) == {
        "forgeeval://forge_eval_evidence_bundle/eb-1",
        "forgemath://forgemath_evaluation/ev-1",
        "cloud://neuroforge/p-1",
    }


def test_driver_fails_closed_when_no_admissible_records():
    # only a non-eval lineage node + no cloud -> nothing admissible
    with pytest.raises(NoAdmittedSourcesError):
        ForgeHQFeedDriver().run(
            "empty-run",
            lineage_nodes=[{"node_type": "forgehq_signal_intake", "node_id": "x"}],
        )
