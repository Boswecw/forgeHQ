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

Tier-A (``resolve_evidence_bundle``): the ``forge_eval_evidence_bundle`` payload
carries the evaluated files directly (``input_contract.target_refs[].file_path``),
so no lineage walk is needed.

Tier-B (``resolve_via_downstream_walk``, P4b-2): for node classes that DON'T carry
a file — e.g. a ``forge_eval_run`` summarising many files — walk the caller-supplied
bounded **downstream** subgraph along allowlisted ``ImpactEdge.v1`` edge types to the
``forge_eval_evidence_bundle`` node(s) that DO carry ``(repo, file)``, then delegate
each to Tier-A. Downstream-only matches DataForge-Local's traversal direction and the
real forge-eval edge ``forge_eval_run --produced--> forge_eval_evidence_bundle``.
forgeHQ still performs no HTTP and owns no paths: the caller supplies the subgraph
(nodes + edges) it read from lineage and the per-bundle ForgeMath gate.
"""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, replace
from typing import Any

# The forge-eval evidence bundle is the Tier-A class: its payload carries
# repository + per-target file paths + the evaluated commit.
FORGE_EVAL_EVIDENCE_BUNDLE_KIND = "forge_eval_evidence_bundle"

# Edge types whose target node "carries / implicates the produced code-target".
# Grounded in the real forge-eval emitter: ``forge_eval_run --produced--> bundle``
# (edge_type="produced", source=run, target=bundle). The walk follows only these.
DEFAULT_CODE_TARGET_EDGE_TYPES = frozenset({"produced"})

# Walk bounds (defensive — the subgraph is caller-supplied but kept finite/cheap).
DEFAULT_MAX_HOPS = 4
DEFAULT_MAX_NODES = 64

# Skip reasons (surfaced so the operator sees *why* a signal produced no fix).
SKIP_UNKNOWN_KIND = "unknown_payload_kind"
SKIP_GATE_NOT_ALLOWED = "gate_not_allowed"
SKIP_NO_TARGETS = "no_target_in_payload"
SKIP_NO_REPOSITORY = "no_repository"
SKIP_NO_WALK_PATH = "no_walk_path"  # walk fully explored, reached no evidence bundle
SKIP_WALK_BUDGET = "walk_budget_exhausted"  # hop/node bound hit before any bundle


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
    resolution: str = "direct"  # "direct" (Tier-A) | "walked" (Tier-B downstream walk)


@dataclass(frozen=True)
class ResolutionResult:
    targets: tuple[ResolvedTarget, ...]
    skipped: tuple[tuple[str, str], ...]  # (identifier, reason)


def _as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _node_kind(node: Mapping[str, Any]) -> str:
    """The node's payload kind, falling back to its lineage ``node_type``."""
    payload = _as_mapping(node.get("payload"))
    return str(payload.get("kind") or node.get("node_type") or "")


def _is_bundle(node: Mapping[str, Any]) -> bool:
    return FORGE_EVAL_EVIDENCE_BUNDLE_KIND in _node_kind(node)


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
    if not _is_bundle(node):
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


def _reachable_bundles(
    seed_id: str,
    *,
    by_id: Mapping[str, Mapping[str, Any]],
    adjacency: Mapping[str, list[str]],
    max_hops: int,
    max_nodes: int,
) -> tuple[list[str], bool]:
    """Bounded BFS downstream from ``seed_id`` over the (already edge-filtered)
    ``adjacency``. Returns the evidence-bundle node ids reached (in first-seen
    order, deduped) and whether the walk was truncated by a hop/node bound.

    The seed itself is never reported as a reachable bundle here (a bundle seed is
    handled before the walk); cycles are neutralised by the ``visited`` set.
    """
    visited: set[str] = {seed_id}
    bundles: list[str] = []
    frontier = [seed_id]
    hops = 0
    truncated = False

    while frontier and hops < max_hops:
        hops += 1
        nxt: list[str] = []
        for src in frontier:
            for dst in adjacency.get(src, ()):  # only allowlisted edges are present
                if dst in visited:
                    continue
                if len(visited) >= max_nodes:
                    truncated = True
                    break
                visited.add(dst)
                node = by_id.get(dst)
                if node is not None and _is_bundle(node):
                    bundles.append(dst)
                nxt.append(dst)
            if truncated:
                break
        frontier = nxt

    if frontier and hops >= max_hops:
        truncated = True  # stopped expanding while edges remained
    return bundles, truncated


def resolve_via_downstream_walk(
    seed_node: Mapping[str, Any],
    *,
    nodes: Sequence[Mapping[str, Any]],
    edges: Sequence[Mapping[str, Any]],
    gate_for: Mapping[str, bool],
    source_ref: str = "",
    edge_type_allowlist: frozenset[str] = DEFAULT_CODE_TARGET_EDGE_TYPES,
    max_hops: int = DEFAULT_MAX_HOPS,
    max_nodes: int = DEFAULT_MAX_NODES,
) -> ResolutionResult:
    """Tier-B: resolve a non-file-carrying seed by walking the caller-supplied
    bounded **downstream** subgraph to its ``forge_eval_evidence_bundle`` node(s),
    then delegating each to Tier-A (``resolve_evidence_bundle``).

    ``nodes``/``edges`` are the lineage subgraph the caller read from DataForge-Local
    (``ImpactEdge.v1`` dicts: ``{source_node_id, target_node_id, edge_type}``). Only
    edges whose ``edge_type`` is in ``edge_type_allowlist`` are traversed. ``gate_for``
    maps a bundle node_id → its ForgeMath ``proposal_candidate_allowed`` decision
    (the caller resolves it from the bundle's own downstream gate); a missing entry
    is treated as **not allowed** (fail-closed).

    A bundle seed delegates straight to Tier-A (no walk). Fails closed: a seed that
    reaches no bundle is skipped with ``no_walk_path`` (fully explored) or
    ``walk_budget_exhausted`` (bound hit first) rather than guessing a file.
    """
    seed_id = str(seed_node.get("node_id") or "")
    ident = source_ref or seed_id or "?"

    # A bundle seed carries its files directly — no walk needed.
    if _is_bundle(seed_node):
        return resolve_evidence_bundle(
            seed_node, gate_allowed=bool(gate_for.get(seed_id, False)), source_ref=source_ref
        )

    if not seed_id:
        return ResolutionResult((), ((ident, SKIP_NO_WALK_PATH),))

    by_id: dict[str, Mapping[str, Any]] = {}
    for node in nodes:
        nid = str(node.get("node_id") or "")
        if nid:
            by_id.setdefault(nid, node)
    by_id.setdefault(seed_id, seed_node)

    adjacency: dict[str, list[str]] = {}
    for edge in edges:
        if str(edge.get("edge_type") or "") not in edge_type_allowlist:
            continue
        src = str(edge.get("source_node_id") or "")
        dst = str(edge.get("target_node_id") or "")
        if src and dst:
            adjacency.setdefault(src, []).append(dst)

    bundle_ids, truncated = _reachable_bundles(
        seed_id, by_id=by_id, adjacency=adjacency, max_hops=max_hops, max_nodes=max_nodes
    )

    if not bundle_ids:
        reason = SKIP_WALK_BUDGET if truncated else SKIP_NO_WALK_PATH
        return ResolutionResult((), ((ident, reason),))

    targets: list[ResolvedTarget] = []
    skipped: list[tuple[str, str]] = []
    for bundle_id in bundle_ids:
        bundle = by_id[bundle_id]
        sub = resolve_evidence_bundle(
            bundle,
            gate_allowed=bool(gate_for.get(bundle_id, False)),
            source_ref=source_ref,
        )
        # Re-tag provenance so the operator sees the target came via a walk, not directly.
        targets.extend(replace(t, resolution="walked") for t in sub.targets)
        # Re-key skips to the bundle node so a multi-bundle walk stays distinguishable
        # (which bundle was gated out / empty), regardless of the seed's source_ref.
        skipped.extend((bundle_id, reason) for _ident, reason in sub.skipped)

    return ResolutionResult(tuple(targets), tuple(skipped))
