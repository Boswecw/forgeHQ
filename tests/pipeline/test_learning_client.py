"""Tests for learning_client — emit CodeFixOutcome to NeuroForge model-outcome ingest."""
import json
from contextlib import contextmanager

from app.drivers import learning_client as lc
from app.schemas.code_fix_outcome import CodeFixOutcome, EvidenceItem


def _outcome(model_id="deepseek-chat"):
    return CodeFixOutcome(
        context_bundle_id="ctxb_1",
        task_intent_id="ti_1",
        model_id=model_id,
        tier="STANDARD",
        routing_cell="code_fix:bugfix_logic:python:local",
        family="code_fix", kind="bugfix_logic", language="python", complexity="local", risk="standard",
        stage="verified",
        evidence=(EvidenceItem(1, "pact_verify", True),),
        reward=0.6,
    )


def test_request_mapping():
    body = lc.outcome_to_request(_outcome())
    assert body["model_id"] == "deepseek-chat"
    assert body["routing_cell"] == "code_fix:bugfix_logic:python:local"
    assert body["reward"] == 0.6
    assert body["stage"] == "verified"
    assert body["source_system"] == "forgehq"


def test_emit_skips_when_no_model_id():
    # nothing to attribute (e.g. deterministic stub) -> skip, don't fail
    assert lc.emit_model_outcome(_outcome(model_id=None)) is None


def test_emit_posts_when_model_present(monkeypatch):
    captured = {}

    class _Resp:
        def read(self):
            return json.dumps({"recorded": True, "shadow": True}).encode()

    @contextmanager
    def _cm():
        yield _Resp()

    def _fake(req, timeout=None):
        captured["url"] = req.full_url
        captured["method"] = req.get_method()
        captured["body"] = json.loads(req.data.decode())
        return _cm()

    monkeypatch.setattr(lc.urllib.request, "urlopen", _fake)
    out = lc.emit_model_outcome(_outcome(), neuroforge_url="http://nf")
    assert out == {"recorded": True, "shadow": True}
    assert captured["method"] == "POST"
    assert captured["url"] == "http://nf/api/v1/learning/model-outcome"
    assert captured["body"]["model_id"] == "deepseek-chat"
