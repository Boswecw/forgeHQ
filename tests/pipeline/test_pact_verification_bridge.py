"""
Tests for PactVerificationBridge — forgeHQ VERIFICATION stage wired to pact.

Hermetic by default: request building, grounding-ref conformance against pact's
*real* schema, fail-closed handle checks, and verdict normalization use an
injected fake verifier. The live pact run is opt-in (FORGEHQ_PACT_LIVE=1) since
pact writes evidence artifacts into its own tree.
"""
import json
import os

import pytest

from app.services.pact_verification_bridge import (
    PactVerificationBridge,
    PactVerificationError,
    grounding_ref,
)


def _handle(bundle_id="ctxb_1122676813da3fb5", bundle_hash="1122676813da3fb5"):
    return {
        "task_intent_id": "ti_codefix_abc123",
        "context_bundle_id": bundle_id,
        "bundle_hash": bundle_hash,
        "freshness_band": "Fresh",
    }


def _grounding():
    return (
        grounding_ref("file://forgehq/app/x.py", source_class="active_scene", excerpt="def f(): ..."),
        grounding_ref("doc://forgehq/SYSTEM.md", source_class="accepted_lore_record", excerpt="repo truth"),
    )


def _verify_kwargs(**over):
    base = dict(
        governed=_handle(),
        grounding_refs=_grounding(),
        task_goal="Verify the proposed fix is grounded in the governed context.",
        instruction_block="Only cite admitted refs.",
        answer_constraints=("no speculation",),
    )
    base.update(over)
    return base


# --------------------------------------------------------------------------- #
# Request building + grounding conformance
# --------------------------------------------------------------------------- #


def test_build_request_binds_to_governed_manifest():
    bridge = PactVerificationBridge(verifier=lambda r: {})
    req = bridge.build_request(**_verify_kwargs())
    assert req["packet_class"] == "answer_packet"
    assert req["execution_mode"] == "replay"
    m = req["context_bundle_manifest"]
    assert m["task_intent_id"] == "ti_codefix_abc123"
    assert m["context_bundle_id"] == "ctxb_1122676813da3fb5"
    assert m["bundle_hash"] == "1122676813da3fb5"
    assert m["freshness_band"] == "Fresh"
    assert len(req["compile_input"]["grounding_refs"]) == 2


def test_grounding_ref_authority_mapping():
    assert grounding_ref("a", source_class="active_scene")["authority_class"] == "primary"
    assert grounding_ref("a", source_class="adjacent_scene_summary_or_clipped_body")["authority_class"] == "secondary"
    assert grounding_ref("a", source_class="accepted_style_rule_record")["authority_class"] == "derived"
    assert grounding_ref("a", source_class="unknown")["authority_class"] == "secondary"


def test_grounding_refs_conform_to_real_pact_schema():
    """Grounding refs we emit must validate against pact's actual contract."""
    try:
        from app.drivers.pact_client import _resolve_pact_root

        schema_path = _resolve_pact_root() / "99-contracts" / "schemas" / "grounding_ref.schema.json"
    except Exception:
        pytest.skip("pact not available")
    if not schema_path.is_file():
        pytest.skip("pact grounding_ref schema not found")

    import jsonschema

    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    for ref in _grounding():
        jsonschema.validate(ref, schema)


# --------------------------------------------------------------------------- #
# Fail-closed: governed handle + inputs
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize(
    "mutate",
    [
        lambda h: h.pop("context_bundle_id"),
        lambda h: h.update(context_bundle_id="bundle-123"),
        lambda h: h.update(bundle_hash="  "),
        lambda h: h.pop("task_intent_id"),
    ],
)
def test_invalid_governed_handle_fails_closed(mutate):
    bridge = PactVerificationBridge(verifier=lambda r: {})
    h = _handle()
    mutate(h)
    with pytest.raises(PactVerificationError):
        bridge.build_request(**_verify_kwargs(governed=h))


def test_no_grounding_fails_closed():
    bridge = PactVerificationBridge(verifier=lambda r: {})
    with pytest.raises(PactVerificationError, match="grounding"):
        bridge.build_request(**_verify_kwargs(grounding_refs=()))


def test_empty_task_goal_fails_closed():
    bridge = PactVerificationBridge(verifier=lambda r: {})
    with pytest.raises(PactVerificationError):
        bridge.build_request(**_verify_kwargs(task_goal="   "))


# --------------------------------------------------------------------------- #
# Verdict normalization + binding integrity (injected verifier)
# --------------------------------------------------------------------------- #


def _fake_success(bundle_id, bundle_hash):
    def _v(request):
        return {
            "ok": True,
            "packet": {
                "packet_id": "pkt_1",
                "context_bundle_id": bundle_id,
                "context_bundle_hash": bundle_hash,
                "task_intent_id": "ti_codefix_abc123",
            },
            "receipt": {"receipt_id": "rcpt_1"},
        }

    return _v


def test_verify_returns_bound_verdict():
    bridge = PactVerificationBridge(verifier=_fake_success("ctxb_1122676813da3fb5", "1122676813da3fb5"))
    verdict = bridge.verify(**_verify_kwargs())
    assert verdict["ok"] is True
    assert verdict["packet_id"] == "pkt_1"
    assert verdict["receipt_id"] == "rcpt_1"
    assert verdict["context_bundle_id"] == "ctxb_1122676813da3fb5"
    assert verdict["context_bundle_hash"] == "1122676813da3fb5"


def test_verify_rejects_binding_violation():
    # pact "succeeds" but echoes a different bundle → integrity failure, fail closed.
    bridge = PactVerificationBridge(verifier=_fake_success("ctxb_DIFFERENT", "DIFFERENT"))
    with pytest.raises(PactVerificationError, match="not bound"):
        bridge.verify(**_verify_kwargs())


def test_verify_passes_through_safe_failure():
    def _v(request):
        return {
            "ok": False,
            "packet": {
                "failure_packet_id": "fpkt_1",
                "failure_state": "intake_rejection",
                "public_reason_code": "validation_failed",
                "context_bundle_id": "ctxb_1122676813da3fb5",
                "context_bundle_hash": "1122676813da3fb5",
            },
            "receipt": {"receipt_id": "rcpt_x"},
        }

    bridge = PactVerificationBridge(verifier=_v)
    verdict = bridge.verify(**_verify_kwargs())
    assert verdict["ok"] is False
    assert verdict["failure_state"] == "intake_rejection"
    assert verdict["packet_id"] == "fpkt_1"


# --------------------------------------------------------------------------- #
# Opt-in live pact run
# --------------------------------------------------------------------------- #


@pytest.mark.skipif(
    not os.environ.get("FORGEHQ_PACT_LIVE"),
    reason="set FORGEHQ_PACT_LIVE=1 to run the real pact runtime (writes evidence into pact)",
)
def test_live_pact_verification_is_bundle_bound():
    bridge = PactVerificationBridge()  # real pact_client.verify_packet

    v1 = bridge.verify(**_verify_kwargs(governed=_handle("ctxb_aaaa1111bbbb2222", "aaaa1111bbbb2222")))
    assert v1["ok"] is True
    assert v1["context_bundle_id"] == "ctxb_aaaa1111bbbb2222"
    assert v1["context_bundle_hash"] == "aaaa1111bbbb2222"

    # Identity must change when the governed bundle changes (replay-deterministic binding).
    v2 = bridge.verify(**_verify_kwargs(governed=_handle("ctxb_cccc3333dddd4444", "cccc3333dddd4444")))
    assert v2["ok"] is True
    assert v1["packet_id"] != v2["packet_id"]
    assert v1["receipt_id"] != v2["receipt_id"]
