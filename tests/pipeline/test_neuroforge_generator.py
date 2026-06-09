"""Tests for NeuroForgeGenerator — uses NeuroForge's chat ladder; surfaces model/tier.

No live service: urllib.request.urlopen is monkeypatched. Confirms the request shape
(code-fix prompt, task_type, optional min_tier floor, lineage passthrough), full-file
extraction, and that the ladder's chosen model_id/tier are captured.
"""
import json
from contextlib import contextmanager

import pytest

from app.drivers import neuroforge_generator as ng
from app.drivers.neuroforge_generator import (
    NeuroForgeGenerationError,
    NeuroForgeGenerator,
    _extract_full_file,
)


def _pack():
    return {
        "primary": "def add(a, b):\n    return a + b   ",
        "supporting": ["# repo nav", "ruff check ."],
        "metadata": {
            "task_intent_id": "ti_1",
            "context_bundle_id": "ctxb_1",
            "context_bundle_hash": "h1",
        },
    }


def test_extract_full_file_strips_fences_and_handles_empty():
    assert _extract_full_file("```python\nx = 1\n```") == "x = 1"
    assert _extract_full_file("x = 1\n") == "x = 1"
    assert _extract_full_file("   ") is None
    assert _extract_full_file(None) is None


def test_build_request_shape_and_lineage_and_floor():
    gen = NeuroForgeGenerator(base_url="http://nf")
    body = gen.build_request(
        file_path="app/x.py", current_content="x", directive="fix it",
        pack=_pack(), min_tier="PREMIUM",
    )
    assert body["task_type"] == "code_fix"
    assert body["min_tier"] == "PREMIUM"
    assert body["messages"][0]["role"] == "system"
    assert "app/x.py" in body["messages"][1]["content"]
    # lineage carried so NeuroForge binds inference + learning to the bundle
    assert body["context_bundle_id"] == "ctxb_1"
    assert body["task_intent_id"] == "ti_1"
    assert body["context_bundle_hash"] == "h1"


def test_build_request_omits_min_tier_when_unset():
    body = NeuroForgeGenerator().build_request(
        file_path="a.py", current_content="x", directive="d", pack=_pack(),
    )
    assert "min_tier" not in body  # let the ladder run free by default


def _patch_urlopen(monkeypatch, payload):
    class _Resp:
        def __init__(self, p):
            self._b = json.dumps(p).encode()
        def read(self):
            return self._b

    @contextmanager
    def _cm():
        yield _Resp(payload)

    monkeypatch.setattr(ng.urllib.request, "urlopen", lambda req, timeout=None: _cm())


def test_generate_with_metadata_captures_model_and_tier(monkeypatch):
    _patch_urlopen(monkeypatch, {
        "content": "```python\ndef add(a, b):\n    return a + b\n```",
        "model_id": "deepseek-chat", "tier": "STANDARD",
    })
    gen = NeuroForgeGenerator(base_url="http://nf")
    res = gen.generate_with_metadata(file_path="app/x.py", current_content="x", directive="d", pack=_pack())
    assert res.content == "def add(a, b):\n    return a + b"
    assert res.model_id == "deepseek-chat"
    assert res.tier == "STANDARD"
    # generate() returns just the content (Protocol contract)
    assert gen.generate(repository="r", file_path="app/x.py", current_content="x", directive="d", pack=_pack()) == res.content


def test_generate_raises_on_transport_error(monkeypatch):
    def _boom(req, timeout=None):
        raise OSError("connection refused")

    monkeypatch.setattr(ng.urllib.request, "urlopen", _boom)
    with pytest.raises(NeuroForgeGenerationError):
        NeuroForgeGenerator().generate_with_metadata(
            file_path="a.py", current_content="x", directive="d", pack=_pack(),
        )
