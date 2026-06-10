"""End-to-end orchestrator test (stubbed collaborators — no live model/pact/DataForge)."""
from app.drivers.neuroforge_generator import GenerationResult
from app.services.ai_shaper_service import AiShaperService
from app.services.pact_verification_bridge import PactVerificationBridge
from app.services.self_healing_runner import SelfHealingRunner

CTXB = "ctxb_run_smoke_abc1"


class _FakeContext:
    """Stub context-runtime: assemble returns a dirty target; payloads carry content."""

    def assemble(self, *, repo_id, repo_root, target_file):
        return {
            "task_intent_id": "ti_codefix_run",
            "context_bundle_id": CTXB,
            "bundle_hash": "run_smoke_abc1",
            "manifest": {"freshness_band": "Fresh"},
            "context_item_refs": [f"file://{repo_id}/{target_file}", f"doc://{repo_id}/SYSTEM.md"],
        }

    def fetch_payload(self, *, context_bundle_id, ref):
        if ref.startswith("file://"):
            return {"role": "target", "source_class": "active_scene",
                    "content": "def add(a, b):\n    return a + b   "}  # trailing ws -> hygiene fix
        return {"role": "repo_truth", "source_class": "accepted_lore_record", "content": "# system doc"}


class _FakeNeuroForgeGen:
    def __init__(self, model_id="deepseek-chat", tier="STANDARD"):
        self.model_id, self.tier = model_id, tier

    def generate_with_metadata(self, *, file_path, current_content, directive, pack, min_tier=None):
        return GenerationResult(content="def add(a, b):\n    return a + b\n",
                                model_id=self.model_id, tier=self.tier, raw={})


def _ok_verifier():
    def _v(req):
        m = req["context_bundle_manifest"]
        return {"ok": True, "packet": {"packet_id": "p1", "context_bundle_id": m["context_bundle_id"],
                "context_bundle_hash": m["bundle_hash"], "task_intent_id": m["task_intent_id"]},
                "receipt": {"receipt_id": "r1"}}
    return PactVerificationBridge(verifier=_v)


def _runner(emitted, published, proposed):
    shaper = AiShaperService(
        generator=_FakeNeuroForgeGen(),
        verifier=_ok_verifier(),
        publisher=lambda env: (proposed.append(env), {"status": "pending"})[1],
    )
    return SelfHealingRunner(
        context=_FakeContext(),
        shaper=shaper,
        publish_pack=lambda body: (published.append(body), {"status": "stored"})[1],
        emit_outcome=emitted.append,
    )


def test_full_run_classifies_publishes_emits_and_proposes():
    emitted, published, proposed = [], [], []
    runner = _runner(emitted, published, proposed)
    res = runner.run(repository="forgehq", repo_root="/repo", target_file="app/x.py", raw_kind="trailing_whitespace")

    # classified
    assert res.classification.kind == "hygiene"
    assert res.classification.routing_cell == "code_fix:hygiene:python:trivial"
    assert res.classification.context_bundle_id == CTXB
    # governed handle threaded through
    assert res.governed["context_bundle_id"] == CTXB
    # pack published to the store
    assert res.pack_published is True and len(published) == 1
    assert published[0]["context_pack_id"] == CTXB
    # proposed (verified)
    assert res.shape.proposed is True and len(proposed) == 1
    # learning outcome emitted with the captured model + cell
    assert len(emitted) == 1
    o = emitted[0]
    assert o.model_id == "deepseek-chat"
    assert o.routing_cell == "code_fix:hygiene:python:trivial"
    assert o.reward == 0.6  # verified


def test_run_emits_outcome_even_when_not_proposed():
    emitted, published, proposed = [], [], []

    def _failing(req):
        return {"ok": False, "packet": {"failure_packet_id": "f", "failure_state": "intake_rejection"},
                "receipt": {"receipt_id": "r"}}

    shaper = AiShaperService(generator=_FakeNeuroForgeGen(), verifier=PactVerificationBridge(verifier=_failing),
                             publisher=lambda env: (proposed.append(env), {})[1])
    runner = SelfHealingRunner(context=_FakeContext(), shaper=shaper,
                               publish_pack=lambda b: {"status": "stored"}, emit_outcome=emitted.append)
    res = runner.run(repository="forgehq", repo_root="/repo", target_file="app/x.py", raw_kind="bugfix")
    assert res.shape.proposed is False        # fail-closed: not proposed
    assert proposed == []
    assert len(emitted) == 1 and emitted[0].reward == 0.0  # but the matrix still learns


def test_pack_publish_failure_is_non_fatal():
    # Publishing the governed pack is a durability side-channel; its failure must NOT
    # abort the run or block the learning outcome.
    emitted, proposed = [], []

    def _boom(_body):
        raise RuntimeError("DataForge-Local context-pack store unavailable (404)")

    shaper = AiShaperService(
        generator=_FakeNeuroForgeGen(),
        verifier=_ok_verifier(),
        publisher=lambda env: (proposed.append(env), {"status": "pending"})[1],
    )
    runner = SelfHealingRunner(
        context=_FakeContext(), shaper=shaper, publish_pack=_boom, emit_outcome=emitted.append
    )
    res = runner.run(repository="forgehq", repo_root="/repo", target_file="app/x.py", raw_kind="trailing_whitespace")

    assert res.pack_published is False
    assert res.pack_publish_error and "404" in res.pack_publish_error
    # the run still completed: proposed + emitted despite the pack-publish failure
    assert res.shape.proposed is True and len(proposed) == 1
    assert len(emitted) == 1 and emitted[0].model_id == "deepseek-chat"
