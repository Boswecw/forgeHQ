"""Self-healing feed — resolve admitted signals to targets and run the real fix loop.

Transport-free orchestration (forgeHQ feed plan P4b): for each caller-supplied
item — a forge-eval evidence-bundle lineage node + its ForgeMath gate decision
(``gate_allowed``) + the local ``repo_root`` the caller resolved from FC's registry
— resolve the concrete fix targets (``signal_target_resolver``) and drive the
proven ``SelfHealingRunner`` per target.

The runner is injectable (``TargetRunner``), so the feed loop is unit-testable
without live context-runtime / NeuroForge / DataForge-Local. forgeHQ stays
transport-free and path-agnostic: it never reads lineage over HTTP and never
derives ``repo_root`` itself — the caller supplies both. Fail-closed: ungated /
unresolvable signals and items missing ``repo_root`` are skipped with a reason,
never guessed; a runner exception is captured per target and never aborts the batch.
"""
from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from typing import Any, Protocol

from app.services.signal_target_resolver import (
    ResolutionResult,
    resolve_evidence_bundle,
    resolve_via_downstream_walk,
)

SKIP_NO_REPO_ROOT = "no_repo_root"


class TargetRunner(Protocol):
    """The proven self-healing loop. ``SelfHealingRunner`` satisfies this."""

    def run(
        self,
        *,
        repository: str,
        repo_root: str,
        target_file: str,
        raw_kind: str = ...,
        secondary_raw_kinds: tuple[str, ...] = ...,
        commit_sha: str = ...,
        publish: bool = ...,
    ) -> Any: ...


@dataclass(frozen=True)
class FeedItemResult:
    source_ref: str
    repository: str
    target_file: str
    ran: bool
    error: str | None = None
    result: Any | None = None


@dataclass(frozen=True)
class FeedResult:
    ran: tuple[FeedItemResult, ...]
    skipped: tuple[tuple[str, str], ...]  # (identifier, reason)


def _resolve_item(item: Mapping[str, Any], *, source_ref: str) -> ResolutionResult:
    """Tier-A or Tier-B per item shape (fail-closed either way).

    Tier-B (downstream lineage walk) is opt-in: an item that supplies both
    ``subgraph_nodes`` and ``subgraph_edges`` is resolved by walking to its
    evidence-bundle node(s), with ``gate_by_node_id`` carrying the per-bundle
    ForgeMath gate. Otherwise the item is the Tier-A direct evidence-bundle shape
    (``node`` + single ``gate_allowed``), unchanged.
    """
    node = item.get("node") if isinstance(item.get("node"), Mapping) else {}
    sub_nodes = item.get("subgraph_nodes")
    sub_edges = item.get("subgraph_edges")
    if isinstance(sub_nodes, list) and isinstance(sub_edges, list):
        gate_by_node_id = item.get("gate_by_node_id")
        gate_for = gate_by_node_id if isinstance(gate_by_node_id, Mapping) else {}
        return resolve_via_downstream_walk(
            node,
            nodes=sub_nodes,
            edges=sub_edges,
            gate_for=gate_for,
            source_ref=source_ref,
        )
    return resolve_evidence_bundle(
        node, gate_allowed=bool(item.get("gate_allowed")), source_ref=source_ref
    )


def run_feed(
    items: Iterable[Mapping[str, Any]],
    *,
    runner: TargetRunner,
    publish: bool = True,
) -> FeedResult:
    """Resolve each item's signal to targets and run the fix loop per target.

    Tier-A item: ``{ source_ref, node, gate_allowed, repo_root }`` — ``node`` is the
    forge-eval evidence-bundle lineage node; ``gate_allowed`` is the ForgeMath
    ``proposal_candidate_allowed`` decision; ``repo_root`` is the caller-resolved
    local path for the signal's repository.

    Tier-B item (opt-in, P4b-2): additionally supplies ``subgraph_nodes`` +
    ``subgraph_edges`` (the lineage subgraph) and ``gate_by_node_id`` (per-bundle
    gate); ``node`` is the non-file-carrying seed (e.g. a ``forge_eval_run``).
    """
    ran: list[FeedItemResult] = []
    skipped: list[tuple[str, str]] = []

    for item in items:
        source_ref = str(item.get("source_ref") or "")
        repo_root = str(item.get("repo_root") or "")

        resolution = _resolve_item(item, source_ref=source_ref)
        skipped.extend(resolution.skipped)

        for target in resolution.targets:
            ident = target.source_ref or target.target_file
            if not repo_root:
                # The caller must resolve repository→repo_root (registry); forgeHQ won't guess.
                skipped.append((ident, SKIP_NO_REPO_ROOT))
                continue
            try:
                result = runner.run(
                    repository=target.repository,
                    repo_root=repo_root,
                    target_file=target.target_file,
                    raw_kind=target.raw_kind,
                    secondary_raw_kinds=target.secondary_raw_kinds,
                    commit_sha=target.commit_sha,
                    publish=publish,
                )
                ran.append(
                    FeedItemResult(source_ref, target.repository, target.target_file, True, None, result)
                )
            except Exception as exc:  # noqa: BLE001 - captured per target, never aborts the batch
                ran.append(
                    FeedItemResult(
                        source_ref,
                        target.repository,
                        target.target_file,
                        False,
                        f"{type(exc).__name__}: {exc}",
                    )
                )

    return FeedResult(tuple(ran), tuple(skipped))
