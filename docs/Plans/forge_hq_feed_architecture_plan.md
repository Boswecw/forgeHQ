# forgeHQ Feed Architecture & Completion Plan

> How forgeHQ is fed (cloud + local), what is built today, and the bounded path
> to a fully-fed shaping pipeline. Companion to `forgehq-system-role.md`.
>
> Status: 2026-06-08. Slices A + B (the source feeders) are landed; the rest is
> planned, phase-bounded work.

## 1. Purpose

forgeHQ is the bounded **proposal-generation and confidence-shaping** subsystem:
*"reviewable candidates without counterfeit authority."* It **consumes** upstream
outputs and **shapes** reviewable candidates; it never mints upstream truth or
holds approval authority (see `forgehq-system-role.md`).

This document defines **what feeds forgeHQ** — from cloud and local sources —
and the path from today's state to a fully-driven feed.

## 2. The intended end-to-end feed

```
SOURCES (producers)                 FEEDERS              INTAKE          PIPELINE                 DOWNSTREAM
─────────────────────               ───────────          ──────          ────────                 ──────────
forge-eval   (lineage outputs)  ─┐  EvalSourceFeeder  ┐
ForgeMath    (lineage outputs)  ─┤  (forgeeval://,    ├─ source_refs ─▶ SignalIntake ─▶ ranking ─▶ … ─▶ ForgeHQProposal ─▶ FC read models
ForgeCommand (cloud_proposals)  ─┤   forgemath://)    │   admit_signals   → SignalSnapshot   (shaping stages)              (forgehq lane)
                                 │  CloudSourceFeeder ┘   (admissible by
                                 └  (cloud://)             URI scheme)
```

Authority classes at intake (`app/domain/signals/enums.py`):

| Source | Scheme | Authority class |
|---|---|---|
| forge-eval (deterministic evidence) | `forgeeval://` | `deterministic_evidence` |
| ForgeMath (governed math) | `forgemath://` | `governed_math` |
| ForgeCommand cloud proposals | `cloud://` | `weak_signal` (advisory) |
| ecosystem weak signals | `signal://` | `weak_signal` |
| anything else | — | `unknown` → rejected (fail-closed) |

**Feed policy (chosen):** *all* forge-eval / ForgeMath evaluation outputs become
signals; reviewability decides downstream what is reviewable. Cloud proposals are
weak advisory signals — forgeHQ never treats them as authoritative.

## 3. What exists today

**Built (this work):**
- `SignalIntakeService` (Phase 2) — real admission + classification, fail-closed.
- `EvalSourceFeeder` (slice A) — forge-eval / ForgeMath outputs → admissible refs.
- `cloud://` scheme + `CloudSourceFeeder` (slice B) — cloud proposals → admissible
  refs. Verified: a mixed cloud + eval batch is admitted in one intake.
- DataForge-Local `/api/v1/lineage` surface (separate repo) — durable lineage
  truth the producers (forge-eval/ForgeMath/eval-cal-node) emit their outputs to.
- `ForgeCommandReadModelService` (Phase 6) — forgeHQ's downstream read models;
  the ForgeCommand `forgehq_bridge` lane reads these.

**Not yet built / placeholder:**
- **Producer enumeration** — nothing yet reads producer outputs and constructs
  `EvalOutput` / `CloudProposal` records to hand the feeders. The feeders are
  transport-free by design; their inputs must be supplied.
- **Orchestration is Phase-1 noop** — `ForgeHQOrchestrator` emits *placeholder*
  artifacts at every stage. The per-stage services (`TargetRankingService`, …)
  exist but are not wired into a driven run.
- **No live driver** — forgeHQ is a library: no service entrypoint / job that
  ingests sources and runs a shaping run end-to-end.

## 4. Completion path (phase-bounded)

Each part is bounded to forgeHQ's non-authoritative, fail-closed doctrine. Do not
add API/persistence/orchestration ahead of the phase that calls for it.

**P1 — Source feeders (DONE: slices A + B).** Eval-family + cloud → admissible
refs → real intake.

**P2 — Producer enumeration adapters (DONE).** P2a: DataForge-Local
`GET /api/v1/lineage/nodes?node_type=&source_system=` list-by-type read. P2b:
`app/services/producer_enumeration.py` pure mappers — lineage node →
`EvalOutput` (`forge_eval_*` / `forgemath_*`), cloud record → `CloudProposal`.
Transport-free (a driver supplies the records).

**P3 — Drive the real intake stage (DONE).** `ForgeHQOrchestrator.advance_signal_intake`
/ `run_from_signals` emit the real `SignalSnapshot` from `admit_signals` at
`SIGNAL_INTAKE` (exactly one `SIGNAL_SNAPSHOT`, fail-closed), then placeholder the
rest — the proposal traces to a real snapshot.

**P4a — Bounded driver (DONE).** `app/orchestration/forgehq_feed_driver.py`
`ForgeHQFeedDriver`: producer records → enumerate (P2) → feed (P1) → real-intake
run (P3). Transport-free; the caller supplies lineage nodes / cloud records.

**P4b — De-noop the shaping stages (REMAINING — proposal-shaping intelligence).**
Wire the real per-stage services (ranking → context → design → generation →
falsification → verification → packaging) so the run produces real shaped
candidates, not placeholders. This is the proposal-generation product phase (the
services exist + are non-authoritative, but need real shaping inputs — ranking
factors, designs, patches — likely AI-assisted per §12); it is NOT a wiring slice
and must not be faked. Plus a live entrypoint (service entrypoint or
invoked job) that: enumerate sources → feed → run → emit `ForgeHQProposal` →
publish read models for the ForgeCommand forgehq lane.

## 5. Boundaries / non-goals

- forgeHQ does not persist canonical truth (DataForge is the persistence
  boundary) and does not hold approval/merge authority (ForgeCommand is the
  operator surface). Cloud proposals remain advisory; forge-eval/ForgeMath remain
  the upstream authorities forgeHQ may not overwrite.
- The cloud feed is forgeHQ-intake-side here. A separate, already-discussed option
  is forwarding cloud proposals into the ForgeCommand `healing_proposals` lane;
  that is a different surface and out of scope for this plan.

## 6. Open decisions

- **Lineage list-by-type** on DataForge-Local (needed by P2 eval enumeration) —
  add a `GET /api/v1/lineage/nodes?node_type=…` read, or push from producers.
- **Cloud read path** — pull from the FC-server cloud-proposals API vs. a
  handoff-driven push (`cloud_proposal_handoffs.handoff_target = forgehq`).
- **Driver placement** — forgeHQ as a small invoked job vs. a long-running
  service; both must stay within the non-authoritative boundary.
