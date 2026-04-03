# forgeHQ Extended Roadmap

**Document version:** 1.1 (2026-04-03) — Phase roadmap plus QA foundation

## Current status

| Phase | Status | Outcome |
| --- | --- | --- |
| Phase 0 | Complete | Governance boundaries, artifact vocabularies, reviewability posture, and worker boundaries are implemented |
| Documentation adoption | Complete | Repo now carries the protocol-required documentation stack and build surfaces |
| QA protocol foundation | Complete | Repo now has a truthful test plan, T0 pre-flight, smoke suite, and tier applicability mapping |
| Phase 1 | Complete | No-op but valid shaping pipeline, schema stubs, and strict stage routing are implemented |
| Phase 2+ | Not started | Downstream service slices remain design-only |

## Phase 0 — Boundary Freeze

**Goal:** lock role, non-goals, artifact families, reviewability doctrine, and non-authoritative language.

**Delivered:**

- canonical enums for artifacts, stages, workers, and reviewability
- artifact family registry
- worker ownership registry
- reviewability/language posture helpers
- system-role and contract docs

**Exit condition:** no ambiguity remains about what forgeHQ owns.

## Documentation Adoption

**Goal:** bring the repo into compliance with the documentation protocol before broader implementation work.

**Delivered:**

- `CLAUDE.md`
- modular `doc/system/` source
- `doc/system/BUILD.sh`
- generated root `SYSTEM.md`
- `scripts/context-bundle.sh`
- architecture spec and extended roadmap docs
- documentation verification tests

**Exit condition:** repo truth can be rebuilt, selectively loaded, and validated through versioned documentation surfaces.

## QA Protocol Foundation

**Goal:** close audit-identified QA gaps before expanding runtime scope.

**Delivered:**

- `FORGEHQ_COMPREHENSIVE_TEST_PLAN.md`
- `docs/qa/` checklist, findings log template, run-report template, and tier applicability matrix
- `scripts/qa-mode-a-preflight.sh`
- `scripts/qa-regression-smoke.sh`
- QA foundation contract tests

**Exit condition:** forgeHQ can execute a truthful Mode A pre-flight and classify deferred tiers without fabricating unsupported coverage.

## Phase 1 — Core Artifact and Orchestrator Skeleton

**Goal:** create a no-op but valid staged pipeline with strict stage progression and fail-closed behavior.

**Delivered:**

- shaping run model
- stage router
- orchestrator skeleton
- worker interface contracts
- schema stubs for all core artifacts
- invalid transition protection
- pipeline tests for valid progression and blocked transitions

**Exit condition:** a target can traverse all stages with placeholder artifacts and strict validation.

## Phase 2 — Ranking and Context Slice

**Goal:** select one target and build a bounded context bundle.

**Deliverables:**

- signal intake service
- admissibility validator
- target ranking service
- ranking trace artifact
- context bundle builder
- source-ref validation
- scope boundary enforcement

**Exit condition:** one target can be selected and packaged with valid lineage and scope.

## Phase 3 — Design and Generation Slice

**Goal:** enforce design-before-generation.

**Deliverables:**

- candidate design service
- design schema and validators
- generator contract
- DataForge-first adapter entry
- out-of-scope rejection logic
- candidate patch artifact wiring

**Exit condition:** generation is impossible before a valid design artifact exists.

## Phase 4 — Critic and Verification Slice

**Goal:** make proposals challengeable and measurable.

**Deliverables:**

- falsification worker
- contradiction checks
- duplicate-test detection hooks
- downgrade logic
- candidate verification harness
- gain plus limitation recording
- fail-closed handling for missing measurement basis

**Exit condition:** the system can classify proposals as weak, mixed, or strong enough for review.

## Phase 5 — Proposal Packaging and Persistence Slice

**Goal:** assemble and persist a complete reviewable proposal backbone.

**Deliverables:**

- confidence shaping summary builder
- forgehq proposal builder
- optional evidence bundle builder
- DataForge persistence wiring
- lineage edge persistence
- reviewability state computation

**Exit condition:** one proposal persists with full backbone and computed reviewability state.

## Phase 6 — ForgeCommand Integration Slice

**Goal:** expose queue and detail read models for human review.

**Deliverables:**

- queue read model
- detail read model
- evidence, challenge, and risk separation
- action-state support
- blocked-approval guard when not reviewable

**Exit condition:** a real proposal can be rendered in ForgeCommand with layered review posture.

## Phase 7 — Hardening and Scale-Out

**Goal:** expand safely to wider ecosystem use.

**Deliverables:**

- NeuroForge adapter
- ForgeAgents adapter
- Rake adapter
- invalidation propagation
- supersession handling
- historical outcome feedback hooks

**Exit condition:** forgeHQ is stable enough for bounded ecosystem rollout without role drift.
