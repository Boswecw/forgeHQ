"""forgeHQ producer CLI — run one real self-healing fix end to end.

The spawnable entrypoint Forge_Command's self-healing tick invokes per target. It
wires the live runner (`build_live_runner`): classify -> assemble governed context
-> publish pack -> generate via NeuroForge's ladder (model captured) -> pact-verify
-> emit CodeFixOutcome to NeuroForge (teach the matrix) -> propose. A structured
JSON result is printed to stdout so the caller can capture it as evidence.

The NeuroForge ingest key is read from the environment (NEUROFORGE_API_KEY /
NEUROFORGE_SERVICE_KEY) by learning_client; Forge_Command injects it at spawn so
the secret never lands in a forgeHQ file.

Exit codes (so the spawning tick can react without parsing stdout):
  0  ran to completion; learning outcome emitted (or skipped — no model to attribute)
  1  hard failure — the run raised (e.g. context-runtime unreachable)
  3  ran + verified/proposed, but the learning emit failed (e.g. 401 ingest key)

Stdlib-only (argparse + json), same posture as the drivers.

Run:  python -m app self-heal --repo <id> --repo-root <path> --target <file>
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any

from app.drivers.learning_client import DEFAULT_NEUROFORGE_URL
from app.schemas.code_fix_outcome import CodeFixOutcome
from app.services.self_healing_runner import RunResult, build_live_runner

DEFAULT_CONTEXT_RUNTIME_URL = "http://127.0.0.1:8011"


def _emit_json(payload: dict[str, Any]) -> None:
    # default=str keeps StrEnum / unexpected values serializable rather than crashing.
    json.dump(payload, sys.stdout, default=str)
    sys.stdout.write("\n")


def _result_to_json(result: RunResult, captured: dict[str, Any]) -> dict[str, Any]:
    c = result.classification
    shape = result.shape
    outcome: CodeFixOutcome | None = captured.get("outcome")
    emitted = "outcome" in captured
    return {
        "status": "completed",
        "proposed": shape.proposed,
        "classification": {
            "routing_cell": c.routing_cell,
            "family": c.family,
            "kind": c.kind,
            "language": c.language,
            "complexity": c.complexity,
            "risk": c.risk,
            "min_tier": c.min_tier,
            "method": c.classification_method,
            "confidence": c.confidence,
        },
        "governed": {
            "context_bundle_id": result.governed.get("context_bundle_id"),
            "task_intent_id": result.governed.get("task_intent_id"),
            "bundle_hash": result.governed.get("bundle_hash"),
            "freshness_band": result.governed.get("freshness_band"),
        },
        "pack_published": result.pack_published,
        "shape": {"proposed": shape.proposed, "reason": shape.reason},
        "model_id": outcome.model_id if outcome is not None else None,
        "reward": outcome.reward if outcome is not None else None,
        "outcome_stage": outcome.stage if outcome is not None else None,
        "emit": {
            "attempted": emitted,
            "skipped_no_model": bool(emitted and outcome is not None and outcome.model_id is None),
            "response": captured.get("response"),
            "error": captured.get("error"),
        },
    }


def run_self_heal(args: argparse.Namespace) -> int:
    captured: dict[str, Any] = {}

    def _on_outcome(outcome: CodeFixOutcome, response: Any, error: str | None) -> None:
        captured["outcome"] = outcome
        captured["response"] = response
        captured["error"] = error

    builder_kwargs: dict[str, Any] = {
        "context_runtime_url": args.context_runtime_url,
        "neuroforge_url": args.neuroforge_url,
        "max_source_age_minutes": args.max_source_age_minutes,
        "on_outcome": _on_outcome,
    }
    if args.dataforge_local_url:
        builder_kwargs["dataforge_url"] = args.dataforge_local_url
    runner = build_live_runner(**builder_kwargs)

    try:
        result = runner.run(
            repository=args.repo,
            repo_root=args.repo_root,
            target_file=args.target,
            raw_kind=args.raw_kind,
            secondary_raw_kinds=tuple(args.secondary_raw_kinds),
            files_changed=args.files_changed,
            lines_changed=args.lines_changed,
            commit_sha=args.commit,
            publish=not args.no_publish,
        )
    except Exception as exc:  # noqa: BLE001 - report, never crash the spawning tick
        _emit_json({"status": "error", "stage": "run", "error": f"{type(exc).__name__}: {exc}"})
        return 1

    _emit_json(_result_to_json(result, captured))
    return 3 if captured.get("error") else 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="app", description="forgeHQ operational entrypoints.")
    sub = parser.add_subparsers(dest="command", required=True)

    sh = sub.add_parser("self-heal", help="Run one self-healing fix end to end.")
    sh.add_argument("--repo", required=True, help="Repository id (logical name).")
    sh.add_argument("--repo-root", required=True, help="Absolute path to the repo working tree.")
    sh.add_argument("--target", required=True, help="Target file to heal (repo-relative).")
    sh.add_argument("--raw-kind", default="", help="Raw signal kind hint for classification.")
    sh.add_argument(
        "--secondary-raw-kind",
        action="append",
        default=[],
        dest="secondary_raw_kinds",
        help="Additional raw kind (repeatable).",
    )
    sh.add_argument("--files-changed", type=int, default=None)
    sh.add_argument("--lines-changed", type=int, default=None)
    sh.add_argument("--commit", default="unknown", help="Commit sha for provenance.")
    sh.add_argument("--no-publish", action="store_true", help="Shape + emit but do not publish.")
    sh.add_argument(
        "--context-runtime-url",
        default=os.getenv("FORGEHQ_CONTEXT_RUNTIME_URL", DEFAULT_CONTEXT_RUNTIME_URL),
    )
    sh.add_argument("--dataforge-local-url", default=os.getenv("FORGEHQ_DATAFORGE_LOCAL_URL"))
    sh.add_argument(
        "--neuroforge-url",
        default=os.getenv("FORGEHQ_NEUROFORGE_URL", DEFAULT_NEUROFORGE_URL),
    )
    sh.add_argument("--max-source-age-minutes", type=int, default=None)
    sh.set_defaults(func=run_self_heal)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
