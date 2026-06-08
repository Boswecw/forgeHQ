"""Tests for CloudSourceFeeder + the cloud:// scheme — cloud -> forgeHQ intake.

Covers the cloud:// scheme classification (weak/advisory), ref construction,
fail-closed validation, and the integration wire: cloud proposals are admitted
by the real SignalIntakeService — alongside forge-eval / ForgeMath — so forgeHQ
is fed from cloud AND local in one intake.
"""
import pytest

from app.domain.signals.enums import SourceAuthorityClass, classify_source_authority
from app.services.cloud_source_feeder import CloudProposal, CloudSourceFeeder
from app.services.eval_source_feeder import EvalSourceFeeder
from app.services.signal_intake_service import SignalIntakeService


# ---------------------------------------------------------------------------
# cloud:// scheme + ref construction
# ---------------------------------------------------------------------------


def test_cloud_scheme_classifies_as_weak_signal():
    assert (
        classify_source_authority("cloud://neuroforge/p-1")
        == SourceAuthorityClass.WEAK_SIGNAL
    )


def test_cloud_proposal_builds_ref():
    ref = CloudSourceFeeder.proposal("p-1", service="neuroforge").to_source_ref()
    assert ref == "cloud://neuroforge/p-1"


def test_empty_proposal_id_rejected():
    with pytest.raises(ValueError):
        CloudProposal(proposal_id="", service="neuroforge").to_source_ref()


def test_default_service_is_unknown():
    assert CloudProposal(proposal_id="p-2").to_source_ref() == "cloud://unknown/p-2"


# ---------------------------------------------------------------------------
# collect + intake integration
# ---------------------------------------------------------------------------


def test_collect_maps_all_proposals_preserving_order():
    feeder = CloudSourceFeeder()
    refs = feeder.collect_source_refs(
        (feeder.proposal("p-1", "neuroforge"), feeder.proposal("p-2", "dataforge"))
    )
    assert refs == ("cloud://neuroforge/p-1", "cloud://dataforge/p-2")


def test_cloud_refs_admitted_by_signal_intake():
    feeder = CloudSourceFeeder()
    refs = feeder.collect_source_refs((feeder.proposal("p-1", "neuroforge"),))
    snapshot, diagnostics = SignalIntakeService().admit_signals("run-cloud", refs)
    assert snapshot.placeholder is False
    assert set(snapshot.admitted_source_refs) == set(refs)
    assert diagnostics.rejected_count == 0


def test_cloud_and_eval_feed_one_intake_together():
    """forgeHQ fed from cloud AND local (forge-eval/ForgeMath) in a single intake."""
    cloud = CloudSourceFeeder()
    eval_feeder = EvalSourceFeeder()
    refs = (
        cloud.collect_source_refs((cloud.proposal("p-1", "neuroforge"),))
        + eval_feeder.collect_source_refs(
            (
                eval_feeder.forgeeval_output("forge_eval_evidence_bundle", "eb-1"),
                eval_feeder.forgemath_output("forgemath_evaluation", "ev-1"),
            )
        )
    )
    snapshot, diagnostics = SignalIntakeService().admit_signals("run-mixed", refs)
    assert diagnostics.admitted_count == 3
    assert diagnostics.rejected_count == 0
    assert set(snapshot.admitted_source_refs) == set(refs)
