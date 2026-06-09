"""
Tests for the context_client driver — request shaping + parsing, no live service.

urllib.request.urlopen is monkeypatched so these stay hermetic; the live
crossing is exercised by context-runtime's own smoke + the C3 e2e.
"""
import json
from contextlib import contextmanager

import pytest

from app.drivers import context_client


class _FakeResponse:
    def __init__(self, payload: dict):
        self._body = json.dumps(payload).encode("utf-8")

    def read(self):
        return self._body


@contextmanager
def _fake_urlopen_factory(captured: dict, payload: dict):
    def _fake_urlopen(request, timeout=None):
        captured["url"] = request.full_url
        captured["method"] = request.get_method()
        captured["timeout"] = timeout
        if request.data is not None:
            captured["body"] = json.loads(request.data.decode("utf-8"))

        @contextmanager
        def _cm():
            yield _FakeResponse(payload)

        return _cm()

    yield _fake_urlopen


def test_assemble_builds_post_request_and_parses(monkeypatch):
    captured: dict = {}
    result_payload = {"context_bundle_id": "ctxb_abc", "bundle_hash": "abc", "context_item_refs": []}
    with _fake_urlopen_factory(captured, result_payload) as fake:
        monkeypatch.setattr(context_client.urllib.request, "urlopen", fake)
        out = context_client.assemble_context_bundle(
            repo_id="forgehq",
            repo_root="/repo",
            target_file="app/x.py",
            context_runtime_url="http://127.0.0.1:8011",
            max_source_age_minutes=999,
        )

    assert out == result_payload
    assert captured["method"] == "POST"
    assert captured["url"] == "http://127.0.0.1:8011/v1/context/assemble"
    assert captured["body"]["repo_id"] == "forgehq"
    assert captured["body"]["target_file"] == "app/x.py"
    assert captured["body"]["max_source_age_minutes"] == 999
    assert captured["body"]["task_family"] == "code_fix"


def test_assemble_omits_age_when_not_set(monkeypatch):
    captured: dict = {}
    with _fake_urlopen_factory(captured, {"context_bundle_id": "ctxb_x"}) as fake:
        monkeypatch.setattr(context_client.urllib.request, "urlopen", fake)
        context_client.assemble_context_bundle(
            repo_id="forgehq", repo_root="/repo", target_file="app/x.py"
        )
    assert "max_source_age_minutes" not in captured["body"]


def test_fetch_payload_url_encodes_ref(monkeypatch):
    captured: dict = {}
    with _fake_urlopen_factory(captured, {"payload_ref": "file://forgehq/app/x.py"}) as fake:
        monkeypatch.setattr(context_client.urllib.request, "urlopen", fake)
        out = context_client.fetch_payload(
            "ctxb_abc",
            "file://forgehq/app/x.py",
            context_runtime_url="http://127.0.0.1:8011",
        )

    assert out["payload_ref"] == "file://forgehq/app/x.py"
    assert captured["method"] == "GET"
    # The ref query param must be percent-encoded (no raw '://').
    assert "ref=file%3A%2F%2Fforgehq%2Fapp%2Fx.py" in captured["url"]
    assert captured["url"].startswith("http://127.0.0.1:8011/v1/context/ctxb_abc/payload?ref=")
