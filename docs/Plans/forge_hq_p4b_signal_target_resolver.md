# forgeHQ P4b — Signal→Target Resolver (design)

**Status:** Candidate (operator approval required before build)
**Date:** 2026-06-13
**Extends:** `docs/Plans/forge_hq_feed_architecture_plan.md` (this is the first concrete piece of **P4b — de-noop the shaping stages**).
**Doctrine:** forgeHQ stays **transport-free, non-authoritative, fail-closed, phase-bounded** (CLAUDE.md). It proposes; it never mints upstream truth, performs HTTP, or owns persistence.

---

## 1. Problem

Two paths exist today and are **not joined**:

- **`SelfHealingRunner`** (the `self-heal` CLI) — the *real, proven* fix loop (classify → context-runtime → NeuroForge ladder → pact-verify → emit learning → propose). It needs a **concrete target**: `(repository, repo_root, target_file, raw_kind)`.
- **`ForgeHQFeedDriver`** — enumerates real signals (forge-eval/ForgeMath lineage nodes + FC cloud-proposal records) into **`source_refs`** (`scheme://output_type/output_id`) and routes them into the **placeholder** `ShapingRun`.

A `source_ref` resolves only to a **lineage node reference**, not to a file. **The missing intelligence is: `source_ref` → concrete `(repository, target_file, raw_kind)`.** That resolver is this design.

---

## 2. Inputs / outputs (the contract)

**Input (caller-supplied, transport-free):** admitted `source_ref`s plus the lineage records they reference. Per doctrine forgeHQ does **not** fetch lineage; the caller (FC's self-healing tick, reading DataForge-Local `GET /api/v1/lineage/nodes` / `/{id}/downstream`) supplies:
- the referenced node: `{ node_id, node_type, payload_schema_id, payload, source_system, … }`
- optionally a bounded **downstream/upstream subgraph** (nodes + `ImpactEdge.v1` edges) for multi-hop resolution.

**Output:** zero or more
```
ResolvedTarget {
  repository: str           # logical repo id (from the signal)
  target_file: str          # repo-relative path the signal implicates
  raw_kind: str             # classification hint derived from node_type/payload
  secondary_raw_kinds: [..] # optional
  commit_sha: str | "unknown"
  provenance: { source_ref, node_id, resolution: "direct" | "walked", hops }
}
```
`repo_root` is **not** forgeHQ's to know (it's a local filesystem path). The **caller** maps `repository → repo_root` via FC's **registry repo-map** (the registry owns the repo→local-path inventory, worktree/submodule-aware) and invokes `SelfHealingRunner` per `ResolvedTarget`. forgeHQ stays path-agnostic.

**Fail-closed:** a `source_ref` that does not resolve to a concrete, single, in-repo file is **skipped**, never guessed — with a recorded reason (`no_target_in_payload`, `ambiguous_multi_file`, `no_walk_path`, `unknown_payload_schema`). Ambiguity is a skip, not a heuristic.

---

## 3. Resolution strategy (two tiers)

**Tier A — direct payload (P4b-1, first slice).** For node classes whose `payload` already carries the target, read it directly — deterministic, no graph walk:
- candidate fields (to confirm at build against real payload schemas): `payload.repository` / `payload.repo_id`, `payload.file_path` / `payload.target_file` / `payload.location.file`.
- a registry of `payload_schema_id → extractor` keeps this typed and explicit; unknown schemas fail-closed.

**Tier B — lineage walk (P4b-2).** For node classes that don't carry a file (e.g. a `forge_eval_run` summarising many files), walk `ImpactEdge.v1` edges (caller-supplied subgraph) toward the **code-target node** that does carry `(repo, file)`. Bounded: max hops, only follow allowlisted `edge_type`s that mean "implicates code," fail-closed if the walk yields zero or >1 distinct file targets.

**Cloud proposals (P4b-3, weakest).** `proposal_id → (repo, file)` only if the cloud-proposal record carries them; otherwise skip (advisory-only signal, no synthesis).

---

## 4. Where it lives + how it plugs in

- New transport-free service `app/services/signal_target_resolver.py` — pure mapping `(source_ref, supplied records) → tuple[ResolvedTarget, …]` + skip reasons. Mirrors `producer_enumeration.py`'s pure-mapper posture.
- The **feed driver** gains a real path: `enumerate → resolve → run` — for each `ResolvedTarget`, call the existing `SelfHealingRunner` (the proven loop) instead of the placeholder `ShapingRun`. This is the actual **P4b de-noop** for the resolvable classes; unresolved signals stay on the placeholder/skip path.
- A CLI surface (`python -m app self-heal-feed`, or `--from-lineage`) takes caller-supplied records and runs the resolved targets, printing per-target JSON results (same evidence shape as `self-heal`). FC's tick supplies records + the repo-map.
- **No new authority, persistence, or HTTP in forgeHQ.** Proposals still flow only through the existing `healing_publisher` → DataForge-Local `healing-proposals` → FC `/self-healing` hub.

---

## 5. Phasing (each shippable, fail-closed)

- **P4b-1** — Tier-A direct-payload resolver for ONE narrow, confirmed node class end-to-end (real signal → resolved target → `SelfHealingRunner` → real proposal in the hub). Proves the join.
- **P4b-2** — Tier-B bounded lineage walk for classes without a direct file.
- **P4b-3** — cloud-proposal resolution (advisory).
- Throughout: skip-with-reason telemetry so the operator sees *why* a signal didn't produce a fix.

---

## 6. Open questions (confirm at build)

1. **Which `payload_schema_id`s carry `(repo, file)` directly?** Need real forge-eval/ForgeMath node payloads from DataForge-Local lineage to fix the Tier-A extractor registry (the first narrow class).
2. **Which `edge_type`s mean "implicates this code file"?** Defines the Tier-B walk allowlist.
3. **Who supplies the walk subgraph** — does FC's tick pass a bounded downstream set, or just the seed node (Tier-A only for now)? (Transport-free says caller supplies; Tier-A needs only the seed node.)
4. **`raw_kind` mapping** — node_type/payload → the classifier's `raw_kind` hints (so risk floor + routing are right).
5. **repo_root source** — confirm FC registry exposes repo_id → local path for the tick to resolve (the registry repo-map field).

---

## 7. Non-negotiables

- Transport-free, non-authoritative, fail-closed (skip ambiguous; never guess a file).
- forgeHQ never learns/owns local paths; the caller maps repo→root via the registry.
- Real fixes flow only through the proven `SelfHealingRunner` + `healing_publisher`; the resolver only *chooses targets*.
- Proposal lifecycle stays separate from operator decision state (decision happens at the FC hub).
