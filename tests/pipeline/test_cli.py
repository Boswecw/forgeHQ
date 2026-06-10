"""forgeHQ producer CLI tests — arg wiring, JSON shape, emit status, exit codes.

The live drivers are never touched: `build_live_runner` is monkeypatched with a
fake builder that records the kwargs it was handed and drives the `on_outcome`
observer, so we exercise app/cli.py without a model/pact/DataForge/NeuroForge.
"""
from types import SimpleNamespace

import json

import pytest

from app import cli
from app.services.self_healing_runner import RunResult


def _classification(**over):
    base = dict(
        routing_cell="code_fix:hygiene:python:trivial",
        family="code_fix",
        kind="hygiene",
        language="python",
        complexity="trivial",
        risk="low",
        min_tier=None,
        classification_method="deterministic_rule",
        confidence=1.0,
    )
    base.update(over)
    return SimpleNamespace(**base)


def _run_result(*, proposed=True, reason="proposed", pack_published=True):
    return RunResult(
        classification=_classification(),
        governed={
            "context_bundle_id": "ctxb_run_x",
            "task_intent_id": "ti_codefix_run",
            "bundle_hash": "run_x",
            "freshness_band": "Fresh",
        },
        shape=SimpleNamespace(proposed=proposed, reason=reason),
        pack_published=pack_published,
    )


def _outcome(model_id="deepseek-chat", reward=0.6, stage="verified"):
    return SimpleNamespace(model_id=model_id, reward=reward, stage=stage)


def _install_fake_builder(monkeypatch, *, run_result=None, exc=None, emit=None):
    """Patch cli.build_live_runner; capture kwargs and drive the observer.

    ``emit`` is (outcome, response, error) to pass to on_outcome, or None to skip.
    ``exc`` (if set) is raised from runner.run to exercise the hard-failure path.
    """
    seen = {}

    def _fake_build(**kwargs):
        seen["kwargs"] = kwargs
        on_outcome = kwargs.get("on_outcome")

        class _Runner:
            def run(self, **run_kwargs):
                seen["run_kwargs"] = run_kwargs
                if emit is not None and on_outcome is not None:
                    on_outcome(*emit)
                if exc is not None:
                    raise exc
                return run_result if run_result is not None else _run_result()

        return _Runner()

    monkeypatch.setattr(cli, "build_live_runner", _fake_build)
    return seen


BASE_ARGS = ["self-heal", "--repo", "forgehq", "--repo-root", "/repo", "--target", "app/x.py"]


def test_parser_wires_target_and_url_defaults(monkeypatch):
    monkeypatch.delenv("FORGEHQ_CONTEXT_RUNTIME_URL", raising=False)
    monkeypatch.delenv("FORGEHQ_NEUROFORGE_URL", raising=False)
    args = cli.build_parser().parse_args(BASE_ARGS + ["--raw-kind", "trailing_whitespace"])
    assert args.repo == "forgehq" and args.repo_root == "/repo" and args.target == "app/x.py"
    assert args.raw_kind == "trailing_whitespace"
    assert args.context_runtime_url == cli.DEFAULT_CONTEXT_RUNTIME_URL
    assert args.neuroforge_url == cli.DEFAULT_NEUROFORGE_URL


def test_run_success_emits_json_and_exit_0(monkeypatch, capsys):
    seen = _install_fake_builder(
        monkeypatch, emit=(_outcome(), {"accepted": True}, None)
    )
    rc = cli.main(BASE_ARGS + ["--raw-kind", "trailing_whitespace"])
    assert rc == 0

    out = json.loads(capsys.readouterr().out)
    assert out["status"] == "completed" and out["proposed"] is True
    assert out["classification"]["routing_cell"] == "code_fix:hygiene:python:trivial"
    assert out["model_id"] == "deepseek-chat" and out["reward"] == 0.6
    assert out["emit"]["attempted"] is True and out["emit"]["error"] is None
    assert out["emit"]["skipped_no_model"] is False
    # the observer was actually wired through the builder
    assert "on_outcome" in seen["kwargs"]
    # target args threaded into runner.run
    assert seen["run_kwargs"]["target_file"] == "app/x.py"


def test_emit_failure_returns_exit_3(monkeypatch, capsys):
    _install_fake_builder(
        monkeypatch, emit=(_outcome(), None, "HTTPError: 401 Unauthorized")
    )
    rc = cli.main(BASE_ARGS)
    assert rc == 3  # ran, but the ingest emit failed — actionable for the operator
    out = json.loads(capsys.readouterr().out)
    assert out["status"] == "completed"
    assert out["emit"]["error"] == "HTTPError: 401 Unauthorized"


def test_skip_when_no_model(monkeypatch, capsys):
    _install_fake_builder(
        monkeypatch, emit=(_outcome(model_id=None, reward=0.0), None, None)
    )
    rc = cli.main(BASE_ARGS)
    assert rc == 0
    out = json.loads(capsys.readouterr().out)
    assert out["model_id"] is None and out["emit"]["skipped_no_model"] is True


def test_hard_failure_returns_exit_1(monkeypatch, capsys):
    _install_fake_builder(monkeypatch, exc=RuntimeError("context-runtime unreachable"))
    rc = cli.main(BASE_ARGS)
    assert rc == 1
    out = json.loads(capsys.readouterr().out)
    assert out["status"] == "error" and "context-runtime unreachable" in out["error"]


def test_not_proposed_still_exit_0(monkeypatch, capsys):
    _install_fake_builder(
        monkeypatch,
        run_result=_run_result(proposed=False, reason="verification failed: not ok"),
        emit=(_outcome(reward=0.0, stage="verified"), {"accepted": True}, None),
    )
    rc = cli.main(BASE_ARGS)
    assert rc == 0  # a verify-fail still ran + emitted; the matrix learned the failure
    out = json.loads(capsys.readouterr().out)
    assert out["proposed"] is False and out["reward"] == 0.0
