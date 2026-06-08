"""Tests for EvalSourceFeeder — forge-eval / ForgeMath -> forgeHQ intake.

Covers ref construction for both eval-family schemes, the "all evaluation
outputs" feed policy, fail-closed validation, and the integration wire: every
feeder-produced ref is admitted by the real SignalIntakeService.
"""
import pytest

from app.domain.signals.enums import SourceAuthorityClass, classify_source_authority
from app.services.eval_source_feeder import EvalOutput, EvalSourceFeeder
from app.services.signal_intake_service import SignalIntakeService


# ---------------------------------------------------------------------------
# Ref construction
# ---------------------------------------------------------------------------


def test_forgeeval_output_builds_deterministic_evidence_ref():
    out = EvalSourceFeeder.forgeeval_output("forge_eval_evidence_bundle", "eb-1")
    ref = out.to_source_ref()
    assert ref == "forgeeval://forge_eval_evidence_bundle/eb-1"
    assert classify_source_authority(ref) == SourceAuthorityClass.DETERMINISTIC_EVIDENCE


def test_forgemath_output_builds_governed_math_ref():
    out = EvalSourceFeeder.forgemath_output("forgemath_evaluation", "ev-1")
    ref = out.to_source_ref()
    assert ref == "forgemath://forgemath_evaluation/ev-1"
    assert classify_source_authority(ref) == SourceAuthorityClass.GOVERNED_MATH


def test_unknown_scheme_is_rejected():
    with pytest.raises(ValueError):
        EvalOutput("bugcheck", "finding", "f-1").to_source_ref()


def test_empty_output_fields_are_rejected():
    with pytest.raises(ValueError):
        EvalOutput("forgeeval", "", "x").to_source_ref()
    with pytest.raises(ValueError):
        EvalOutput("forgeeval", "t", "").to_source_ref()


# ---------------------------------------------------------------------------
# Feed policy: ALL evaluation outputs -> source refs
# ---------------------------------------------------------------------------


def test_collect_maps_all_outputs_preserving_order():
    feeder = EvalSourceFeeder()
    outputs = (
        feeder.forgeeval_output("forge_eval_run", "run-1"),
        feeder.forgeeval_output("forge_eval_evidence_bundle", "eb-1"),
        feeder.forgemath_output("forgemath_output", "out-1"),
        feeder.forgemath_output("forgemath_runtime_admission", "adm-1"),
    )
    refs = feeder.collect_source_refs(outputs)
    assert refs == (
        "forgeeval://forge_eval_run/run-1",
        "forgeeval://forge_eval_evidence_bundle/eb-1",
        "forgemath://forgemath_output/out-1",
        "forgemath://forgemath_runtime_admission/adm-1",
    )


def test_collect_fails_closed_on_inadmissible_ref():
    feeder = EvalSourceFeeder()
    with pytest.raises(ValueError):
        feeder.collect_source_refs((EvalOutput("weak", "signal", "s-1"),))


# ---------------------------------------------------------------------------
# Integration wire: feeder refs are admitted by the real intake service
# ---------------------------------------------------------------------------


def test_feeder_refs_are_admitted_by_signal_intake():
    feeder = EvalSourceFeeder()
    outputs = (
        feeder.forgeeval_output("forge_eval_evidence_bundle", "eb-1"),
        feeder.forgemath_output("forgemath_evaluation", "ev-1"),
    )
    refs = feeder.collect_source_refs(outputs)

    snapshot, diagnostics = SignalIntakeService().admit_signals("run-eval", refs)

    assert snapshot.placeholder is False
    assert set(snapshot.admitted_source_refs) == set(refs)
    assert snapshot.rejected_source_refs == ()
    assert diagnostics.admitted_count == 2
    assert diagnostics.rejected_count == 0
