"""
Tests for AiShaperService — the self-healing GENERATION stage end to end.

Hermetic: generator, pact verifier, pack fetcher, and publisher are all injected,
so context -> generate -> verify -> propose is proven without a live model, pact
runtime, or DataForge.
"""
import pytest

from app.services.ai_shaper_service import (
    AiShaperService,
    DeterministicHygieneGenerator,
    ShaperError,
)
from app.services.pact_verification_bridge import PactVerificationBridge


def _governed():
    return {
        "task_intent_id": "ti_codefix_abc",
        "context_bundle_id": "ctxb_1122676813da3fb5",
        "bundle_hash": "1122676813da3fb5",
        "freshness_band": "Fresh",
    }


def _dirty_pack():
    # primary has trailing whitespace + no final newline -> hygiene generator fixes it
    return {
        "primary": "def add(a, b):\n    return a + b   ",
        "supporting": ["# repo nav", "ruff check ."],
        "metadata": {"context_bundle_id": "ctxb_1122676813da3fb5"},
    }


def _clean_pack():
    return {"primary": "def ok():\n    return 1\n", "supporting": [], "metadata": {}}


def _ok_verifier():
    def _v(request):
        m = request["context_bundle_manifest"]
        return {
            "ok": True,
            "packet": {
                "packet_id": "pkt_1",
                "context_bundle_id": m["context_bundle_id"],
                "context_bundle_hash": m["bundle_hash"],
                "task_intent_id": m["task_intent_id"],
            },
            "receipt": {"receipt_id": "rcpt_1"},
        }

    return PactVerificationBridge(verifier=_v)


def _failing_verifier():
    def _v(request):
        return {
            "ok": False,
            "packet": {"failure_packet_id": "f1", "failure_state": "intake_rejection"},
            "receipt": {"receipt_id": "r1"},
        }

    return PactVerificationBridge(verifier=_v)


def _capturing_publisher():
    captured = {}

    def _pub(envelope):
        captured["envelope"] = envelope
        return {"proposal_id": envelope["event_id"], "status": "pending"}

    return _pub, captured


# --------------------------------------------------------------------------- #
# Happy path: generate -> verify -> propose
# --------------------------------------------------------------------------- #


def test_shapes_verifies_and_publishes_a_proposal():
    pub, captured = _capturing_publisher()
    svc = AiShaperService(
        generator=DeterministicHygieneGenerator(),
        verifier=_ok_verifier(),
        publisher=pub,
    )
    result = svc.shape(
        repository="forgehq",
        file_path="app/x.py",
        governed=_governed(),
        pack=_dirty_pack(),
    )
    assert result.proposed is True
    assert result.publish_response == {"proposal_id": result.envelope["event_id"], "status": "pending"}

    env = captured["envelope"]
    assert env["schema_version"] == "healing.code_fix.v1"
    # full corrected file is carried (the bridge applies content, not a patch)
    assert env["payload"]["proposed_edit"]["content"].endswith("return a + b\n")
    # verification + context evidence rides in the envelope
    assert env["payload"]["verification"] == {
        "verifier": "pact", "ok": True, "packet_id": "pkt_1", "receipt_id": "rcpt_1",
    }
    assert env["payload"]["context"]["context_bundle_id"] == "ctxb_1122676813da3fb5"
    assert env["payload"]["context"]["context_bundle_hash"] == "1122676813da3fb5"
    assert env["payload"]["context"]["served_from"] == "precomputed_pact_packet"


def test_shape_without_publish_returns_envelope_only():
    svc = AiShaperService(verifier=_ok_verifier())
    result = svc.shape(
        repository="forgehq", file_path="app/x.py",
        governed=_governed(), pack=_dirty_pack(), publish=False,
    )
    assert result.proposed is True
    assert result.envelope is not None
    assert result.publish_response is None


# --------------------------------------------------------------------------- #
# Fail-closed paths: no proposal published
# --------------------------------------------------------------------------- #


def test_no_change_from_generator_is_fail_closed():
    pub, captured = _capturing_publisher()
    svc = AiShaperService(verifier=_ok_verifier(), publisher=pub)
    result = svc.shape(
        repository="forgehq", file_path="app/x.py",
        governed=_governed(), pack=_clean_pack(),  # already clean -> hygiene no-op
    )
    assert result.proposed is False
    assert "no change" in result.reason
    assert "envelope" not in captured  # nothing published


def test_failed_verification_blocks_proposal():
    pub, captured = _capturing_publisher()
    svc = AiShaperService(verifier=_failing_verifier(), publisher=pub)
    result = svc.shape(
        repository="forgehq", file_path="app/x.py",
        governed=_governed(), pack=_dirty_pack(),
    )
    assert result.proposed is False
    assert "verification failed" in result.reason
    assert result.verdict["ok"] is False
    assert "envelope" not in captured  # fail-closed: not published


def test_empty_primary_is_fail_closed():
    svc = AiShaperService(verifier=_ok_verifier())
    result = svc.shape(
        repository="forgehq", file_path="app/x.py",
        governed=_governed(), pack={"primary": "", "supporting": [], "metadata": {}},
        publish=False,
    )
    assert result.proposed is False
    assert "empty precomputed context" in result.reason


def test_invalid_governed_handle_raises():
    svc = AiShaperService(verifier=_ok_verifier())
    bad = _governed()
    bad["context_bundle_id"] = "nope"
    with pytest.raises(ShaperError):
        svc.shape(repository="forgehq", file_path="app/x.py", governed=bad, pack=_dirty_pack())


def test_fetches_pack_by_id_when_not_supplied():
    """The consumer wire: shaper fetches the precomputed pack by bundle id."""
    fetched = {}

    def _fetcher(bundle_id):
        fetched["id"] = bundle_id
        return _dirty_pack()

    svc = AiShaperService(verifier=_ok_verifier(), pack_fetcher=_fetcher, publisher=lambda e: {"status": "pending"})
    result = svc.shape(repository="forgehq", file_path="app/x.py", governed=_governed())
    assert result.proposed is True
    assert fetched["id"] == "ctxb_1122676813da3fb5"
