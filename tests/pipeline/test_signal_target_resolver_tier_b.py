"""P4b-2 Tier-B signal→target resolver: downstream lineage walk → bundle → Tier-A.

A non-file-carrying seed (e.g. ``forge_eval_run``) is resolved by walking the
caller-supplied bounded downstream subgraph along allowlisted edge types
(``produced``, the real ``forge_eval_run --produced--> bundle`` edge) to the
evidence-bundle node(s), then delegating each to Tier-A. Exercises the gate
(per-bundle), the edge allowlist, hop/node bounds, cycles, and fail-closed skips.
"""
from __future__ import annotations

from app.services.signal_target_resolver import (
    SKIP_GATE_NOT_ALLOWED,
    SKIP_NO_WALK_PATH,
    SKIP_WALK_BUDGET,
    resolve_via_downstream_walk,
)


def _run_node(node_id="run-1"):
    """A forge_eval_run seed — summary node, carries no file."""
    return {"node_id": node_id, "node_type": "forge_eval_run", "payload": {"kind": "forge_eval_run"}}


def _bundle_node(node_id="bundle-1", *, repository_id="ForgeHQ", files=(("app/a.py", "trailing_whitespace"),)):
    return {
        "node_id": node_id,
        "node_type": "forge_eval_evidence_bundle",
        "repository_id": repository_id,
        "payload": {
            "kind": "forge_eval_evidence_bundle",
            "repo_path": "/x/ForgeHQ",
            "head_commit": "abc123",
            "input_contract": {
                "target_refs": [
                    {"target_id": f"t{i}", "file_path": fp, "source_kind": sk}
                    for i, (fp, sk) in enumerate(files)
                ]
            },
        },
    }


def _edge(src, dst, edge_type="produced"):
    return {"source_node_id": src, "target_node_id": dst, "edge_type": edge_type}


def test_run_walks_to_gated_bundle_and_resolves_via_tier_a():
    seed = _run_node()
    bundle = _bundle_node(files=(("app/a.py", "trailing_whitespace"), ("app/b.py", "missing_trailing_newline")))
    result = resolve_via_downstream_walk(
        seed,
        nodes=[seed, bundle],
        edges=[_edge("run-1", "bundle-1")],
        gate_for={"bundle-1": True},
        source_ref="forgeeval://forge_eval_run/run-1",
    )
    assert result.skipped == ()
    assert [(t.target_file, t.raw_kind) for t in result.targets] == [
        ("app/a.py", "trailing_whitespace"),
        ("app/b.py", "missing_trailing_newline"),
    ]
    # Provenance is honest: these came via a walk, not a direct bundle seed.
    assert {t.resolution for t in result.targets} == {"walked"}
    assert {t.repository for t in result.targets} == {"ForgeHQ"}


def test_reached_bundle_with_gate_not_allowed_is_skipped():
    seed = _run_node()
    bundle = _bundle_node()
    result = resolve_via_downstream_walk(
        seed, nodes=[seed, bundle], edges=[_edge("run-1", "bundle-1")], gate_for={"bundle-1": False}
    )
    assert result.targets == ()
    assert result.skipped == (("bundle-1", SKIP_GATE_NOT_ALLOWED),)


def test_missing_gate_entry_fails_closed():
    seed = _run_node()
    bundle = _bundle_node()
    result = resolve_via_downstream_walk(
        seed, nodes=[seed, bundle], edges=[_edge("run-1", "bundle-1")], gate_for={}
    )
    assert result.targets == ()
    assert result.skipped == (("bundle-1", SKIP_GATE_NOT_ALLOWED),)


def test_no_reachable_bundle_skips_no_walk_path():
    seed = _run_node()
    other = {"node_id": "other-1", "node_type": "forge_eval_stage", "payload": {"kind": "forge_eval_stage"}}
    result = resolve_via_downstream_walk(
        seed, nodes=[seed, other], edges=[_edge("run-1", "other-1")], gate_for={}, source_ref="sig://x",
    )
    assert result.targets == ()
    assert result.skipped == (("sig://x", SKIP_NO_WALK_PATH),)


def test_non_allowlisted_edge_is_not_followed():
    seed = _run_node()
    bundle = _bundle_node()
    # An "informed" edge does not imply a produced code-target → not traversed.
    result = resolve_via_downstream_walk(
        seed,
        nodes=[seed, bundle],
        edges=[_edge("run-1", "bundle-1", edge_type="informed")],
        gate_for={"bundle-1": True},
    )
    assert result.targets == ()
    assert result.skipped == (("run-1", SKIP_NO_WALK_PATH),)


def test_hop_budget_exhausted_before_bundle():
    seed = _run_node()
    mid = {"node_id": "mid-1", "node_type": "forge_eval_stage", "payload": {"kind": "forge_eval_stage"}}
    bundle = _bundle_node()
    # run -> mid -> bundle is 2 hops; max_hops=1 stops before the bundle.
    result = resolve_via_downstream_walk(
        seed,
        nodes=[seed, mid, bundle],
        edges=[_edge("run-1", "mid-1"), _edge("mid-1", "bundle-1")],
        gate_for={"bundle-1": True},
        max_hops=1,
    )
    assert result.targets == ()
    assert result.skipped == (("run-1", SKIP_WALK_BUDGET),)
    # With the budget raised, the same subgraph resolves.
    ok = resolve_via_downstream_walk(
        seed,
        nodes=[seed, mid, bundle],
        edges=[_edge("run-1", "mid-1"), _edge("mid-1", "bundle-1")],
        gate_for={"bundle-1": True},
        max_hops=2,
    )
    assert [t.target_file for t in ok.targets] == ["app/a.py"]


def test_cycle_in_subgraph_terminates_and_resolves():
    seed = _run_node()
    bundle = _bundle_node()
    # run <-> loop cycle, plus run -> bundle; the visited set must neutralise the cycle.
    result = resolve_via_downstream_walk(
        seed,
        nodes=[seed, {"node_id": "loop-1", "node_type": "forge_eval_stage", "payload": {"kind": "x"}}, bundle],
        edges=[_edge("run-1", "loop-1"), _edge("loop-1", "run-1"), _edge("run-1", "bundle-1")],
        gate_for={"bundle-1": True},
    )
    assert [t.target_file for t in result.targets] == ["app/a.py"]


def test_multiple_bundles_from_one_run_resolve_in_edge_order():
    seed = _run_node()
    b1 = _bundle_node("bundle-1", files=(("app/a.py", "trailing_whitespace"),))
    b2 = _bundle_node("bundle-2", files=(("app/b.py", "missing_trailing_newline"),))
    result = resolve_via_downstream_walk(
        seed,
        nodes=[seed, b1, b2],
        edges=[_edge("run-1", "bundle-1"), _edge("run-1", "bundle-2")],
        gate_for={"bundle-1": True, "bundle-2": True},
    )
    assert [t.target_file for t in result.targets] == ["app/a.py", "app/b.py"]
    assert {t.resolution for t in result.targets} == {"walked"}


def test_bundle_seed_delegates_to_tier_a_direct():
    bundle = _bundle_node()
    result = resolve_via_downstream_walk(
        bundle, nodes=[bundle], edges=[], gate_for={"bundle-1": True}, source_ref="forgeeval://.../bundle-1"
    )
    assert [t.target_file for t in result.targets] == ["app/a.py"]
    # A bundle seed is resolved directly — no walk happened.
    assert {t.resolution for t in result.targets} == {"direct"}
