"""P4b-1 Tier-A signal→target resolver: forge_eval_evidence_bundle → targets.

Exercises the real evidence-bundle shape (repo + input_contract.target_refs[] +
head_commit), the ForgeMath confidence gate, and fail-closed skips.
"""
from __future__ import annotations

from app.services.signal_target_resolver import (
    SKIP_GATE_NOT_ALLOWED,
    SKIP_NO_REPOSITORY,
    SKIP_NO_TARGETS,
    SKIP_UNKNOWN_KIND,
    resolve_evidence_bundle,
)


def _bundle_node(*, repository_id="ForgeHQ", repo_path="/home/x/forgeHQ", targets=None):
    """A lineage node whose payload is a forge_eval_evidence_bundle."""
    if targets is None:
        targets = [
            {"target_id": "t1", "file_path": "app/a.py", "source_kind": "trailing_whitespace"},
            {"target_id": "t2", "file_path": "app/b.py", "source_kind": "missing_trailing_newline"},
        ]
    return {
        "node_id": "node-0001",
        "node_type": "forge_eval_evidence_bundle",
        "repository_id": repository_id,
        "payload": {
            "schema_version": "v1",
            "kind": "forge_eval_evidence_bundle",
            "run_id": "run-0001",
            "repo_path": repo_path,
            "head_commit": "abc123",
            "input_contract": {
                "schema_version": "ForgeEvalCentipedeInput.v1",
                "target_ref_count": len(targets),
                "target_refs": targets,
                "metadata": {},
            },
        },
    }


def test_gated_bundle_resolves_one_target_per_evaluated_file():
    result = resolve_evidence_bundle(_bundle_node(), gate_allowed=True, source_ref="forgeeval://forge_eval_evidence_bundle/node-0001")
    assert result.skipped == ()
    assert [(t.target_file, t.raw_kind) for t in result.targets] == [
        ("app/a.py", "trailing_whitespace"),
        ("app/b.py", "missing_trailing_newline"),
    ]
    assert {t.repository for t in result.targets} == {"ForgeHQ"}
    assert {t.commit_sha for t in result.targets} == {"abc123"}
    assert all(t.source_ref.endswith("node-0001") for t in result.targets)


def test_ungated_bundle_is_skipped_fail_closed():
    result = resolve_evidence_bundle(_bundle_node(), gate_allowed=False)
    assert result.targets == ()
    assert result.skipped == (("node-0001", SKIP_GATE_NOT_ALLOWED),)


def test_non_bundle_node_is_skipped():
    node = {"node_id": "n2", "node_type": "forgemath_lane_evaluation", "payload": {"kind": "forgemath_lane_evaluation"}}
    result = resolve_evidence_bundle(node, gate_allowed=True)
    assert result.targets == ()
    assert result.skipped == (("n2", SKIP_UNKNOWN_KIND),)


def test_bundle_without_target_files_is_skipped():
    result = resolve_evidence_bundle(_bundle_node(targets=[]), gate_allowed=True)
    assert result.targets == ()
    assert result.skipped == (("node-0001", SKIP_NO_TARGETS),)


def test_repository_falls_back_to_repo_path_basename():
    node = _bundle_node(repository_id="", repo_path="/srv/repos/MyApp")
    result = resolve_evidence_bundle(node, gate_allowed=True)
    assert {t.repository for t in result.targets} == {"MyApp"}


def test_no_repository_anywhere_is_skipped():
    node = _bundle_node(repository_id="", repo_path="")
    result = resolve_evidence_bundle(node, gate_allowed=True)
    assert result.targets == ()
    assert result.skipped == (("node-0001", SKIP_NO_REPOSITORY),)
