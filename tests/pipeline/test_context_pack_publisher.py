"""Tests for context_pack_publisher — builds the NeuroForge read shape from a
context-runtime result and publishes it (POST mocked; no live service)."""
import json
from contextlib import contextmanager

import pytest

from app.drivers import context_pack_publisher as pub


def _assemble_result():
    return {
        "task_intent_id": "ti_codefix_7c6acfda",
        "context_bundle_id": "ctxb_d13c59d092fca8b1",
        "bundle_hash": "d13c59d092fca8b1",
        "manifest": {"freshness_band": "Fresh"},
        "context_item_refs": [
            "file://forgehq/app/x.py",
            "file://forgehq/app/y.py",
            "doc://forgehq/SYSTEM.md",
        ],
    }


def _payloads():
    return {
        "file://forgehq/app/x.py": {
            "role": "target", "source_class": "active_scene",
            "content": "def x(): return 1", "content_hash": "h1",
        },
        "file://forgehq/app/y.py": {
            "role": "adjacent", "source_class": "adjacent_scene_summary_or_clipped_body",
            "content": "def y(): return 2", "content_hash": "h2",
        },
        "doc://forgehq/SYSTEM.md": {
            "role": "repo_truth", "source_class": "accepted_lore_record",
            "content": "# system doc", "content_hash": "h3",
        },
    }


def test_build_pack_body_primary_is_target_supporting_is_rest():
    body = pub.build_pack_body(_assemble_result(), _payloads())
    assert body["context_pack_id"] == "ctxb_d13c59d092fca8b1"
    assert body["bundle_hash"] == "d13c59d092fca8b1"
    assert body["primary"] == "def x(): return 1"  # the target/active_scene
    assert body["supporting"] == ["def y(): return 2", "# system doc"]
    assert body["metadata"]["task_intent_id"] == "ti_codefix_7c6acfda"
    assert body["metadata"]["freshness_band"] == "Fresh"
    assert body["metadata"]["admitted_ref_count"] == 3
    assert "active_scene" in body["metadata"]["source_classes"]


def test_build_pack_body_includes_pact_verdict_when_supplied():
    verdict = {"ok": True, "packet_id": "pkt_1", "receipt_id": "rcpt_1", "raw": {"big": "ignored"}}
    body = pub.build_pack_body(_assemble_result(), _payloads(), pact_verdict=verdict)
    assert body["metadata"]["pact_verdict"] == {
        "ok": True, "packet_id": "pkt_1", "receipt_id": "rcpt_1",
    }


def test_build_pack_body_fails_closed_on_bad_handle():
    bad = _assemble_result()
    bad["context_bundle_id"] = "nope"
    with pytest.raises(pub.ContextPackPublishError):
        pub.build_pack_body(bad, _payloads())


def test_publish_posts_to_dataforge_local(monkeypatch):
    captured: dict = {}

    class _Resp:
        def __init__(self, payload):
            self._b = json.dumps(payload).encode()
        def read(self):
            return self._b

    @contextmanager
    def _cm(payload):
        yield _Resp(payload)

    def _fake_urlopen(request, timeout=None):
        captured["url"] = request.full_url
        captured["method"] = request.get_method()
        captured["body"] = json.loads(request.data.decode())
        return _cm({"context_pack_id": "ctxb_d13c59d092fca8b1", "status": "stored"})

    monkeypatch.setattr(pub.urllib.request, "urlopen", _fake_urlopen)

    body = pub.build_pack_body(_assemble_result(), _payloads())
    out = pub.publish_context_pack(body, dataforge_url="http://127.0.0.1:8005")

    assert out == {"context_pack_id": "ctxb_d13c59d092fca8b1", "status": "stored"}
    assert captured["method"] == "POST"
    assert captured["url"] == "http://127.0.0.1:8005/df/rag/context-pack"
    assert captured["body"]["context_pack_id"] == "ctxb_d13c59d092fca8b1"
    assert captured["body"]["primary"] == "def x(): return 1"
