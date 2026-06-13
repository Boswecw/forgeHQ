"""Signal→Target resolver — P4b-1, Tier-A (direct-payload), transport-free.

Maps an admitted **forge-eval evidence-bundle** lineage node to the concrete
``(repository, target_file, raw_kind)`` targets the proven ``SelfHealingRunner``
consumes — the first real join of the signal feed to the fix loop (forgeHQ feed
plan P4b; see ``docs/Plans/forge_hq_p4b_signal_target_resolver.md``).

Doctrine (CLAUDE.md): forgeHQ stays **non-authoritative + transport-free**. The
caller supplies the node record (read from DataForge-Local lineage) AND the
ForgeMath confidence-gate decision; this module performs no HTTP, owns no local
filesystem paths (the caller maps ``repository`` → ``repo_root`` via FC's registry),
and **fails closed**: an ungated bundle, or one without concrete target files,
yields zero targets with a recorded skip reason rather than a guess.

Tier-A only: the ``forge_eval_evidence_bundle`` payload carries the evaluated files
directly (``input_contract.target_refs[].file_path``), so no lineage walk is
needed. Lineage-walk resolution for classes that don't carry a file is Tier-B (P4b-2).
"""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

# The forge-eval evidence bundle is the Tier-A class: its payload carries
# repository + per-target file paths + the evaluated commit.
FORGE_EVAL_EVIDENCE_BUNDLE_KIND = "forge_eval_evidence_bundle"

# Skip reasons (surfaced so the operator sees *why* a signal produced no fix).
SKIP_UNKNOWN_KIND = "unknown_payload_kind"
SKIP_GATE_NOT_ALLOWED = "gate_not_allowed"
SKIP_NO_TARGETS = "no_target_in_payload"
SKIP_NO_REPOSITORY = "no_repository"


@dataclass(frozen=True)
class ResolvedTarget:
    """A concrete fix target for ``SelfHealingRunner.run``. ``repo_root`` is
    deliberately absent — the caller resolves it from ``repository`` via the
    registry repo-map (forgeHQ never learns local paths)."""

    repository: str
    target_file: str
    raw_kind: str
    commit_sha: str
    source_ref: str
    secondary_raw_kinds: tuple[str, ...] = ()


@dataclass(frozen=True)
class ResolutionResult:
    targets: tuple[ResolvedTarget, ...]
    skipped: tuple[tuple[str, str], ...]  # (identifier, reason)


def _as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _repository_of(node: Mapping[str, Any], payload: Mapping[str, Any]) -> str:
    """Logical repo id. Prefer the lineage node's ``repository_id`` (set by the
    forge-eval emitter); fall back to the payload, then the ``repo_path`` basename
    only as a last resort (``repo_path`` is a filesystem path, not a logical id)."""
    repo = str(node.get("repository_id") or payload.get("repository_id") or "")
    if repo:
        return repo
    repo_path = str(payload.get("repo_path") or "").rstrip("/")
    return repo_path.rsplit("/", 1)[-1] if repo_path else ""


def resolve_evidence_bundle(
    node: Mapping[str, Any],
    *,
    gate_allowed: bool,
    source_ref: str = "",
) -> ResolutionResult:
    """Tier-A: a ``forge_eval_evidence_bundle`` lineage node → one ``ResolvedTarget``
    per evaluated target file — but only when the ForgeMath confidence gate
    (``proposal_candidate_allowed``, supplied by the caller as ``gate_allowed``)
    permitted a proposal. Fails closed otherwise.
    """
    ident = source_ref or str(node.get("node_id") or "?")
    payload = _as_mapping(node.get("payload"))
    kind = str(payload.get("kind") or node.get("node_type") or "")
    if FORGE_EVAL_EVIDENCE_BUNDLE_KIND not in kind:
        return ResolutionResult((), ((ident, SKIP_UNKNOWN_KIND),))
    if not gate_allowed:
        return ResolutionResult((), ((ident, SKIP_GATE_NOT_ALLOWED),))

    repository = _repository_of(node, payload)
    if not repository:
        return ResolutionResult((), ((ident, SKIP_NO_REPOSITORY),))

    commit_sha = str(payload.get("head_commit") or "unknown")
    contract = _as_mapping(payload.get("input_contract"))
    refs = contract.get("target_refs")

    targets: list[ResolvedTarget] = []
    if isinstance(refs, list):
        for ref in refs:
            ref_map = _as_mapping(ref)
            file_path = str(ref_map.get("file_path") or "")
            if not file_path:
                continue
            targets.append(
                ResolvedTarget(
                    repository=repository,
                    target_file=file_path,
                    raw_kind=str(ref_map.get("source_kind") or ""),
                    commit_sha=commit_sha,
                    source_ref=source_ref,
                )
            )

    if not targets:
        return ResolutionResult((), ((ident, SKIP_NO_TARGETS),))
    return ResolutionResult(tuple(targets), ())
