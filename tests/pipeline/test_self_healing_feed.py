"""feed→resolve→run orchestration (P4b-1 wiring), with an injected fake runner.

No live context-runtime / NeuroForge / DataForge-Local: the runner is a stub that
records calls, so this asserts the resolve→run fan-out, gate/skip handling, and
per-target error capture deterministically.
"""
from __future__ import annotations

from app.services.self_healing_feed import SKIP_NO_REPO_ROOT, run_feed
from app.services.signal_target_resolver import SKIP_GATE_NOT_ALLOWED


class _FakeRunner:
    def __init__(self, *, raise_on: str | None = None):
        self.calls: list[dict] = []
        self._raise_on = raise_on

    def run(self, **kwargs):
        self.calls.append(kwargs)
        if self._raise_on is not None and kwargs.get("target_file") == self._raise_on:
            raise RuntimeError("boom")
        return {"shape": type("S", (), {"proposed": True})()}


def _bundle(repository_id="ForgeHQ", targets=(("app/a.py", "trailing_whitespace"), ("app/b.py", "bugfix"))):
    return {
        "node_id": "node-1",
        "node_type": "forge_eval_evidence_bundle",
        "repository_id": repository_id,
        "payload": {
            "kind": "forge_eval_evidence_bundle",
            "repo_path": "/x/ForgeHQ",
            "head_commit": "c1",
            "input_contract": {
                "target_refs": [{"target_id": f"t{i}", "file_path": fp, "source_kind": sk} for i, (fp, sk) in enumerate(targets)]
            },
        },
    }


def _item(**over):
    base = {"source_ref": "forgeeval://forge_eval_evidence_bundle/node-1", "node": _bundle(), "gate_allowed": True, "repo_root": "/repo"}
    base.update(over)
    return base


def test_gated_item_runs_the_loop_per_target():
    runner = _FakeRunner()
    result = run_feed([_item()], runner=runner, publish=False)
    assert [c["target_file"] for c in runner.calls] == ["app/a.py", "app/b.py"]
    assert all(c["repo_root"] == "/repo" and c["repository"] == "ForgeHQ" and c["publish"] is False for c in runner.calls)
    assert [(r.target_file, r.ran) for r in result.ran] == [("app/a.py", True), ("app/b.py", True)]
    assert result.skipped == ()


def test_ungated_item_is_skipped_and_runner_untouched():
    runner = _FakeRunner()
    result = run_feed([_item(gate_allowed=False)], runner=runner)
    assert runner.calls == []
    assert result.ran == ()
    assert result.skipped == (("forgeeval://forge_eval_evidence_bundle/node-1", SKIP_GATE_NOT_ALLOWED),)


def test_missing_repo_root_skips_each_target():
    runner = _FakeRunner()
    result = run_feed([_item(repo_root="")], runner=runner)
    assert runner.calls == []
    assert result.ran == ()
    assert [reason for _, reason in result.skipped] == [SKIP_NO_REPO_ROOT, SKIP_NO_REPO_ROOT]


def test_runner_error_on_one_target_does_not_abort_batch():
    runner = _FakeRunner(raise_on="app/a.py")
    result = run_feed([_item()], runner=runner)
    by_file = {r.target_file: r for r in result.ran}
    assert by_file["app/a.py"].ran is False and "boom" in (by_file["app/a.py"].error or "")
    assert by_file["app/b.py"].ran is True
