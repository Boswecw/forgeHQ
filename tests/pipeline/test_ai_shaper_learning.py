"""The shaper's learning emission: classification floor + model capture + outcome emit."""
from app.schemas.code_fix_classification import CodeFixClassification, RiskFloorResolution
from app.services.ai_shaper_service import AiShaperService
from app.services.code_fix_classifier import CodeFixClassifier
from app.services.pact_verification_bridge import PactVerificationBridge


def _governed():
    return {
        "task_intent_id": "ti_codefix_abc",
        "context_bundle_id": "ctxb_1122676813da3fb5",
        "bundle_hash": "1122676813da3fb5",
        "freshness_band": "Fresh",
    }


def _dirty_pack():
    return {"primary": "def add(a, b):\n    return a + b   ", "supporting": ["x"], "metadata": {}}


class _FakeNeuroForgeGen:
    """Generator exposing generate_with_metadata (model/tier capture path)."""

    def __init__(self, model_id="deepseek-chat", tier="STANDARD"):
        self.model_id = model_id
        self.tier = tier
        self.last_min_tier = "UNSET"

    def generate_with_metadata(self, *, file_path, current_content, directive, pack, min_tier=None):
        from app.drivers.neuroforge_generator import GenerationResult
        self.last_min_tier = min_tier
        return GenerationResult(
            content="def add(a, b):\n    return a + b\n", model_id=self.model_id, tier=self.tier, raw={}
        )


def _ok_verifier():
    def _v(request):
        m = request["context_bundle_manifest"]
        return {"ok": True, "packet": {"packet_id": "p1", "context_bundle_id": m["context_bundle_id"],
                "context_bundle_hash": m["bundle_hash"], "task_intent_id": m["task_intent_id"]},
                "receipt": {"receipt_id": "r1"}}
    return PactVerificationBridge(verifier=_v)


def _failing_verifier():
    def _v(request):
        return {"ok": False, "packet": {"failure_packet_id": "f", "failure_state": "intake_rejection"},
                "receipt": {"receipt_id": "r"}}
    return PactVerificationBridge(verifier=_v)


def _classification(kind="bugfix_logic"):
    return CodeFixClassifier().classify(file_path="app/x.py", raw_kind=kind)


def test_emits_verified_outcome_with_captured_model_on_success():
    emitted = []
    svc = AiShaperService(generator=_FakeNeuroForgeGen(), verifier=_ok_verifier(), publisher=lambda e: {"status": "pending"})
    result = svc.shape(
        repository="forgehq", file_path="app/x.py", governed=_governed(), pack=_dirty_pack(),
        classification=_classification(), outcome_emitter=emitted.append,
    )
    assert result.proposed is True
    assert len(emitted) == 1
    o = emitted[0]
    assert o.model_id == "deepseek-chat"
    assert o.routing_cell.startswith("code_fix:bugfix_logic:python")
    assert o.stage == "verified"
    assert o.reward == 0.6  # verified-pass


def test_emits_outcome_even_on_verify_failure():
    emitted = []
    svc = AiShaperService(generator=_FakeNeuroForgeGen(), verifier=_failing_verifier(), publisher=lambda e: {})
    result = svc.shape(
        repository="forgehq", file_path="app/x.py", governed=_governed(), pack=_dirty_pack(),
        classification=_classification(), outcome_emitter=emitted.append,
    )
    assert result.proposed is False  # fail-closed: no proposal
    assert len(emitted) == 1         # but the outcome is still a learning signal
    assert emitted[0].reward == 0.0  # verify-fail -> zero reward (teaches the matrix)


def test_governance_critical_passes_premium_floor_to_generator():
    gen = _FakeNeuroForgeGen()
    svc = AiShaperService(generator=gen, verifier=_ok_verifier(), publisher=lambda e: {})
    # a security fix -> classification.min_tier == PREMIUM -> passed as NeuroForge floor
    svc.shape(
        repository="forgehq", file_path="app/x.py", governed=_governed(), pack=_dirty_pack(),
        classification=_classification(kind="sql injection"), outcome_emitter=lambda o: None,
    )
    assert gen.last_min_tier == "PREMIUM"


def test_no_emit_without_classification_or_emitter():
    emitted = []
    svc = AiShaperService(generator=_FakeNeuroForgeGen(), verifier=_ok_verifier(), publisher=lambda e: {})
    svc.shape(repository="forgehq", file_path="app/x.py", governed=_governed(), pack=_dirty_pack())
    assert emitted == []  # backward-compatible: no learning wiring -> no emit
