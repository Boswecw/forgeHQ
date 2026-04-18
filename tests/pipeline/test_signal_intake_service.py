"""
Tests for SignalIntakeService — forgeHQ Phase 2.

Covers admissibility classification, source-ref preservation, fail-closed
behavior for unknown schemes, and non-authoritative posture requirements.
"""
import pytest

from app.domain.artifacts.enums import ArtifactAuthorityPosture, ArtifactFamily
from app.domain.signals.enums import AdmissibilityDecision, SourceAuthorityClass
from app.services.signal_intake_service import (
    NoAdmittedSourcesError,
    SignalIntakeService,
)


# ---------------------------------------------------------------------------
# Admissibility classification
# ---------------------------------------------------------------------------


def test_forgeeval_ref_is_admitted():
    svc = SignalIntakeService()
    snapshot, diagnostics = svc.admit_signals(
        run_id="r1",
        source_refs=("forgeeval://coverage/module_a",),
    )
    assert "forgeeval://coverage/module_a" in snapshot.admitted_source_refs
    assert diagnostics.admitted_count == 1
    assert diagnostics.rejected_count == 0


def test_forgemath_ref_is_admitted():
    svc = SignalIntakeService()
    snapshot, _ = svc.admit_signals(
        run_id="r1",
        source_refs=("forgemath://rule/mutation_floor",),
    )
    assert "forgemath://rule/mutation_floor" in snapshot.admitted_source_refs


def test_signal_ref_is_admitted():
    svc = SignalIntakeService()
    snapshot, _ = svc.admit_signals(
        run_id="r1",
        source_refs=("signal://regression/test_suite_a",),
    )
    assert "signal://regression/test_suite_a" in snapshot.admitted_source_refs


def test_http_scheme_is_rejected():
    svc = SignalIntakeService()
    with pytest.raises(NoAdmittedSourcesError):
        svc.admit_signals(
            run_id="r1",
            source_refs=("http://example.com/data",),
        )


def test_bare_string_without_scheme_is_rejected():
    svc = SignalIntakeService()
    with pytest.raises(NoAdmittedSourcesError):
        svc.admit_signals(
            run_id="r1",
            source_refs=("just-a-string",),
        )


def test_unknown_scheme_recorded_in_diagnostics():
    svc = SignalIntakeService()
    with pytest.raises(NoAdmittedSourcesError):
        svc.admit_signals(
            run_id="r1",
            source_refs=("unknown://data/x",),
        )


# ---------------------------------------------------------------------------
# Mixed batches
# ---------------------------------------------------------------------------


def test_mixed_batch_admits_valid_and_rejects_unknown():
    svc = SignalIntakeService()
    snapshot, diagnostics = svc.admit_signals(
        run_id="r1",
        source_refs=(
            "forgeeval://coverage/mod_a",
            "http://bad.example.com",
            "signal://mutation/suite_b",
            "file:///bad/path",
        ),
    )
    assert snapshot.admitted_source_refs == (
        "forgeeval://coverage/mod_a",
        "signal://mutation/suite_b",
    )
    assert snapshot.rejected_source_refs == (
        "http://bad.example.com",
        "file:///bad/path",
    )
    assert diagnostics.admitted_count == 2
    assert diagnostics.rejected_count == 2


def test_rejected_refs_absent_from_source_refs():
    svc = SignalIntakeService()
    snapshot, _ = svc.admit_signals(
        run_id="r1",
        source_refs=("forgeeval://x", "http://bad"),
    )
    assert "http://bad" not in snapshot.source_refs


def test_admissibility_record_details_for_rejected_ref():
    svc = SignalIntakeService()
    snapshot, diagnostics = svc.admit_signals(
        run_id="r1",
        source_refs=("forgeeval://x", "garbage://y"),
    )
    rejected_record = next(
        r for r in diagnostics.records if r.source_ref == "garbage://y"
    )
    assert rejected_record.decision == AdmissibilityDecision.REJECTED
    assert rejected_record.authority_class == SourceAuthorityClass.UNKNOWN
    assert rejected_record.rejection_reason is not None


def test_admissibility_record_details_for_admitted_ref():
    svc = SignalIntakeService()
    _, diagnostics = svc.admit_signals(
        run_id="r1",
        source_refs=("forgeeval://coverage/a",),
    )
    admitted_record = diagnostics.records[0]
    assert admitted_record.decision == AdmissibilityDecision.ADMITTED
    assert admitted_record.authority_class == SourceAuthorityClass.DETERMINISTIC_EVIDENCE
    assert admitted_record.rejection_reason is None


# ---------------------------------------------------------------------------
# Fail-closed behavior
# ---------------------------------------------------------------------------


def test_empty_source_refs_raises_no_admitted_sources():
    svc = SignalIntakeService()
    with pytest.raises(NoAdmittedSourcesError):
        svc.admit_signals(run_id="r1", source_refs=())


def test_all_unknown_refs_raises_no_admitted_sources():
    svc = SignalIntakeService()
    with pytest.raises(NoAdmittedSourcesError):
        svc.admit_signals(
            run_id="r1",
            source_refs=("http://a", "ftp://b", "garbage://c"),
        )


# ---------------------------------------------------------------------------
# Non-authoritative posture
# ---------------------------------------------------------------------------


def test_snapshot_is_not_placeholder():
    svc = SignalIntakeService()
    snapshot, _ = svc.admit_signals(
        run_id="r1",
        source_refs=("forgeeval://x",),
    )
    assert snapshot.placeholder is False


def test_snapshot_authority_posture_is_non_authoritative():
    svc = SignalIntakeService()
    snapshot, _ = svc.admit_signals(
        run_id="r1",
        source_refs=("forgeeval://x",),
    )
    assert snapshot.authority_posture == ArtifactAuthorityPosture.NON_AUTHORITATIVE


def test_snapshot_artifact_family_is_signal_snapshot():
    svc = SignalIntakeService()
    snapshot, _ = svc.admit_signals(
        run_id="r1",
        source_refs=("forgeeval://x",),
    )
    assert snapshot.artifact_family == ArtifactFamily.SIGNAL_SNAPSHOT


def test_diagnostics_artifact_family_is_intake_diagnostics():
    svc = SignalIntakeService()
    _, diagnostics = svc.admit_signals(
        run_id="r1",
        source_refs=("forgeeval://x",),
    )
    assert diagnostics.artifact_family == ArtifactFamily.INTAKE_DIAGNOSTICS


def test_diagnostics_non_authoritative():
    svc = SignalIntakeService()
    _, diagnostics = svc.admit_signals(
        run_id="r1",
        source_refs=("forgeeval://x",),
    )
    assert diagnostics.authority_posture == ArtifactAuthorityPosture.NON_AUTHORITATIVE
