# forgeHQ — VSCode Codex Implementation Package

**Date:** April 3, 2026  
**Time Zone:** America/New_York

---

## Purpose

This document converts the prior ForgeShaping hard plan into an implementation package for **VSCode Codex** using the new repository identity:

- **Old working name:** ForgeShaping
- **Canonical repo name going forward:** **forgeHQ**

forgeHQ is the governed proposal-generation and confidence-shaping subsystem for the BDS ecosystem. It converts bounded evidence and weak-confidence signals into **reviewable candidate improvements**.

It is not deterministic truth.  
It is not approval authority.  
It is not merge authority.  
It is not canonical persistence authority.

---

## 1. Canonical Identity

### Repo name
`forgeHQ`

### System role
forgeHQ is the bounded system that:
- consumes upstream evidence and weak-confidence signals
- ranks candidate improvement targets
- builds bounded context packs
- designs candidate changes before generation
- generates bounded candidate artifacts
- challenges those candidates through falsification
- verifies candidate outcome
- assembles non-authoritative proposal packages for human review

### Hard non-goals
forgeHQ must not:
- claim deterministic repo truth
- overwrite ForgeEval truth
- overwrite ForgeMath truth
- make approval decisions
- silently execute autonomous merges
- collapse proposal state into decision state

---

## 2. System Boundaries

### Upstream dependencies
- **ForgeEval** — deterministic evidence substrate
- **ForgeMath** — canonical math / rule authority where adopted
- ecosystem signals — coverage, mutation, regression, recurrence, burden, exposure, priority, service-adapter policy, historical outcomes

### Downstream dependencies
- **DataForge** — lineage, artifacts, proposal persistence, review linkage, rollback linkage
- **ForgeCommand** — human review surface and recorded operator action state

### Boundary law
forgeHQ may consume ForgeEval artifacts and ForgeMath outputs, but it may not overwrite either as canonical truth.

---

## 3. Core Operating Question

forgeHQ exists to answer one governed question:

> Given bounded evidence and weak-confidence signals, what candidate improvement should be proposed, how should it be challenged, what proof supports it, and is it reviewable by a human operator?

---

## 4. Canonical Pipeline

forgeHQ must be built as a strict staged pipeline.

### Stage 1 — Signal Intake
**Responsibilities**
- validate source admissibility
- preserve source refs
- classify authority posture
- reject semantically unknown or unresolved inputs

**Artifacts**
- `signal_snapshot`
- `intake_diagnostics`

### Stage 2 — Target Ranking
**Responsibilities**
- score candidate targets using governed ranking factors
- separate deterministic evidence from proposal interpretation
- preserve explainability of why a target surfaced

**Artifacts**
- `target_ranking`
- `ranking_factor_trace`

### Stage 3 — Context Curation
**Responsibilities**
- build bounded context for exactly one target at a time
- include only target-relevant code, contracts, failures, lineage, and history
- enforce scope boundary statement
- fail closed if scope exceeds policy

**Artifacts**
- `context_bundle`

### Stage 4 — Candidate Design
**Responsibilities**
- define bounded change hypothesis
- define intended confidence gain
- define targeted behaviors and contracts
- define oracle strategy
- define disconfirming checks
- define failure hypotheses

**Artifacts**
- `candidate_design`

**Hard rule**
No generation without a valid design artifact.

### Stage 5 — Candidate Generation
**Responsibilities**
- generate only inside scope
- preserve parent refs
- enforce service-adapter rules
- reject out-of-scope expansion

**Artifacts**
- `candidate_patch`

### Stage 6 — Falsification / Critic Lane
**Responsibilities**
- search for contradictions
- detect weak assertions
- detect overfitting
- detect duplicate tests
- detect shallow-gain theater
- downgrade weak proposals

**Artifacts**
- `falsification_report`

**Hard rule**
No proposal is reviewable without challenge.

### Stage 7 — Verification Harness
**Responsibilities**
- syntax checks
- import checks
- test execution where applicable
- branch delta measurement where applicable
- mutation delta measurement where applicable
- limitation disclosure

**Artifacts**
- `candidate_verification`

**Hard rule**
Verification must show both what improved and what remained weak.

### Stage 8 — Proposal Packaging
**Responsibilities**
- assemble design, candidate, challenge, verification, confidence summary, residual risk, rollback posture, and lineage refs
- apply non-authoritative language
- compute reviewability state

**Artifacts**
- `confidence_shaping_summary`
- `forgehq_proposal`
- optional `forgehq_evidence_bundle`

---

## 5. Worker Model

forgeHQ must not be implemented as one blended agent.

### Required workers
1. **Signal Analyst**
2. **Context Curator**
3. **Designer**
4. **Generator**
5. **Critic / Falsifier**
6. **Verifier**
7. **Proposal Assembler**
8. **Orchestrator**

### Worker rules
- each worker may emit only its admitted artifact families
- workers must not overwrite canonical upstream artifacts
- orchestrator may sequence stages but may not invent proposal content
- critic posture must remain structurally independent from generator posture

---

## 6. Artifact Backbone

A proposal is only reviewable when the following backbone exists:

1. signal refs
2. target ranking ref
3. context bundle ref
4. candidate design ref
5. candidate patch ref
6. falsification report ref
7. candidate verification ref
8. confidence shaping summary ref
9. parent ForgeEval / ForgeMath refs where applicable
10. final proposal artifact
11. optional evidence bundle

**Hard rule**  
Missing any required backbone artifact forces `not_reviewable`.

---

## 7. Reviewability Contract

A proposal may only be reviewable when all of the following are true:
- design present
- candidate present
- challenge present
- verification present
- non-authoritative notice present
- explicit scope boundary statement present
- parent refs valid
- no unresolved scope escape
- no broken lineage condition

### Automatic non-reviewable conditions
- missing challenge artifact
- missing verification artifact
- missing source refs
- scope escape detected
- invalid parent evidence refs
- confidence summary missing downgrade factors
- rollback class required but absent

---

## 8. Non-Authoritative Language Lock

### Allowed language
- propose
- hypothesize
- suggest
- indicate
- candidate
- challenge
- observed candidate gain
- reviewability state
- residual concern

### Prohibited language
- approved
- confirmed fix
- proven truth
- authoritative state
- must apply
- merge now

### Hard rule
All forgeHQ artifacts must carry explicit non-authoritative posture.

---

## 9. Service Adapter Order

Build shared core first, then adapters in this order:
1. **DataForge**
2. **NeuroForge**
3. **ForgeAgents**
4. **Rake**

### Adapter law
No adapter may broaden shared-core artifact semantics.

---

## 10. Minimum DataForge Persistence Requirements

forgeHQ persistence must preserve three layers:
- deterministic evidence lineage
- non-authoritative proposal lineage
- operator decision lineage

### Minimum persistence objects
- shaping run boundary
- artifact registry rows
- lineage edges
- proposal record
- proposal artifact refs
- eval/math evidence links where applicable
- verification history
- review events
- decision linkage
- rollback linkage where applicable

### Hard rule
Proposal lifecycle state must never be treated as human decision state.

---

## 11. Required Repo Skeleton

This is the recommended initial repo structure for Codex to create.

```text
forgeHQ/
  app/
    api/
    core/
    domain/
      artifacts/
      workers/
      pipeline/
      reviewability/
      adapters/
    schemas/
    services/
    persistence/
    read_models/
    orchestration/
  tests/
    contract/
    pipeline/
    workers/
    persistence/
    read_models/
  docs/
    architecture/
    contracts/
    implementation/
  registry/
  scripts/
  alembic/
```

### Recommended first internal module split

#### `app/domain/artifacts/`
Owns typed artifact models and artifact family enums.

#### `app/domain/pipeline/`
Owns stage definitions, stage transitions, and no-skip pipeline rules.

#### `app/domain/workers/`
Owns worker contracts and allowed emissions.

#### `app/domain/reviewability/`
Owns reviewability rules, downgrade rules, and not-reviewable gates.

#### `app/domain/adapters/`
Owns shared adapter contracts and service-specific policy boundaries.

#### `app/persistence/`
Owns artifact registry writes, lineage edges, proposal rows, and lifecycle separation.

#### `app/read_models/`
Owns ForgeCommand queue/detail read models only.

---

## 12. Phase Plan for Codex Implementation

## Phase 0 — Boundary Freeze
### Goal
Lock role, non-goals, artifact families, reviewability doctrine, and non-authoritative language.

### Codex deliverables
- canonical enums
- artifact family registry
- worker ownership registry
- reviewability state enum
- non-authoritative language constants / validators
- architecture doc for repo truth boundaries

### Exit condition
No ambiguity remains about what forgeHQ owns.

---

## Phase 1 — Core Artifact and Orchestrator Skeleton
### Goal
Create the no-op but valid shaping pipeline.

### Codex deliverables
- shaping run model
- stage enum and stage router
- orchestrator skeleton
- worker interface contracts
- schema stubs for all core artifacts
- fail-closed invalid transition logic

### Exit condition
A target can traverse all stages with placeholder artifacts and strict validation.

---

## Phase 2 — Ranking and Context Slice
### Goal
Make forgeHQ able to select one target and build a bounded context bundle.

### Codex deliverables
- signal intake service
- admissibility validator
- target ranking service
- ranking trace artifact
- context bundle builder
- source-ref validation
- scope boundary enforcement

### Exit condition
One target can be selected and packaged with valid lineage and scope.

---

## Phase 3 — Design and Generation Slice
### Goal
Enforce design-before-generation.

### Codex deliverables
- candidate design service
- design schema and validators
- generator contract
- DataForge-first adapter entry
- out-of-scope rejection logic
- candidate patch artifact wiring

### Exit condition
System can generate only after a valid design artifact exists.

---

## Phase 4 — Critic and Verification Slice
### Goal
Make proposals challengeable and measurable.

### Codex deliverables
- falsification worker
- contradiction checks
- duplicate-test detection hooks
- downgrade logic
- candidate verification harness
- gain + limitation recording
- fail-closed handling for missing measurement basis

### Exit condition
System can determine whether a proposal is weak, mixed, or strong enough for review.

---

## Phase 5 — Proposal Packaging and Persistence Slice
### Goal
Assemble and persist a complete reviewable proposal backbone.

### Codex deliverables
- confidence shaping summary builder
- forgehq proposal artifact builder
- optional evidence bundle builder
- DataForge persistence wiring
- lineage edge persistence
- reviewability state computation

### Exit condition
One proposal persists with full backbone and computed reviewability state.

---

## Phase 6 — ForgeCommand Integration Slice
### Goal
Expose queue and detail read models for human review.

### Codex deliverables
- queue read model
- detail read model
- evidence/challenge/risk separation
- action-state support
- blocked-approval guard when not reviewable

### Exit condition
A real proposal can be rendered in ForgeCommand with layered review posture.

---

## Phase 7 — Hardening and Scale-Out
### Goal
Expand safely to wider ecosystem use.

### Codex deliverables
- NeuroForge adapter
- ForgeAgents adapter
- Rake adapter
- invalidation propagation
- supersession handling
- historical outcome feedback hooks

### Exit condition
forgeHQ is stable enough for bounded ecosystem rollout without role drift.

---

## 13. Exact Files Codex Should Create First

### Governance / contracts
- `docs/architecture/forgehq-system-role.md`
- `docs/contracts/artifact-family-registry.md`
- `docs/contracts/reviewability-contract.md`
- `docs/contracts/non-authoritative-language-policy.md`

### Core enums / types
- `app/domain/artifacts/enums.py`
- `app/domain/pipeline/enums.py`
- `app/domain/reviewability/enums.py`
- `app/domain/workers/enums.py`

### Core schemas
- `app/schemas/shaping_run.py`
- `app/schemas/signal_snapshot.py`
- `app/schemas/target_ranking.py`
- `app/schemas/context_bundle.py`
- `app/schemas/candidate_design.py`
- `app/schemas/candidate_patch.py`
- `app/schemas/falsification_report.py`
- `app/schemas/candidate_verification.py`
- `app/schemas/confidence_shaping_summary.py`
- `app/schemas/forgehq_proposal.py`

### Orchestration
- `app/orchestration/stage_router.py`
- `app/orchestration/forgehq_orchestrator.py`

### Services
- `app/services/signal_intake_service.py`
- `app/services/target_ranking_service.py`
- `app/services/context_bundle_service.py`
- `app/services/candidate_design_service.py`
- `app/services/candidate_generation_service.py`
- `app/services/falsification_service.py`
- `app/services/candidate_verification_service.py`
- `app/services/proposal_packaging_service.py`

### Persistence
- `app/persistence/artifact_registry.py`
- `app/persistence/lineage_repository.py`
- `app/persistence/proposal_repository.py`

### Tests
- `tests/contract/test_artifact_schemas.py`
- `tests/pipeline/test_stage_progression.py`
- `tests/workers/test_worker_emission_boundaries.py`
- `tests/pipeline/test_design_required_before_generation.py`
- `tests/pipeline/test_reviewability_requires_challenge_and_verification.py`

---

## 14. Codex Working Rules for This Repo

These rules should be placed into repo guidance and repeated in implementation prompts.

1. Do not redesign system role.
2. Do not collapse forgeHQ into ForgeEval, ForgeMath, DataForge, or ForgeCommand.
3. Never allow generation without design.
4. Never allow reviewable state without challenge and verification.
5. Preserve explicit upstream truth references.
6. Preserve explicit non-authoritative language posture.
7. Keep proposal lifecycle state separate from operator decision state.
8. Fail closed on missing lineage, invalid refs, scope escape, or invalid stage transitions.
9. Prefer small bounded slices with tests first.
10. Do not invent cross-service semantics not stated in the contracts.

---

## 15. VSCode Codex Prompt Set

Use these prompts one at a time.

---

### Prompt 1 — Phase 0 Boundary Freeze

```text
You are implementing the initial governance slice for a new repo named forgeHQ.

forgeHQ is the bounded proposal-generation and confidence-shaping subsystem in the BDS ecosystem.
It is not deterministic truth.
It is not approval authority.
It is not merge authority.
It is not canonical persistence authority.

Your job in this slice:
1. create the core governance docs and enum scaffolding
2. define artifact families and worker ownership boundaries
3. define reviewability states and non-authoritative language rules
4. do not implement business logic yet

Required constraints:
- forgeHQ may consume ForgeEval evidence and ForgeMath outputs, but may not overwrite either as canonical truth
- no proposal may be reviewable without challenge and verification
- all forgeHQ artifacts must carry explicit non-authoritative posture
- proposal lifecycle state must remain separate from human decision state
- fail closed on ambiguity

Create these files first:
- docs/architecture/forgehq-system-role.md
- docs/contracts/artifact-family-registry.md
- docs/contracts/reviewability-contract.md
- docs/contracts/non-authoritative-language-policy.md
- app/domain/artifacts/enums.py
- app/domain/pipeline/enums.py
- app/domain/reviewability/enums.py
- app/domain/workers/enums.py

Also create minimal tests that validate enum completeness and prohibited state collapse.

Work in small commits, preserve explicit comments where boundary law matters, and do not add speculative features.
```

---

### Prompt 2 — Phase 1 Core Artifact and Orchestrator Skeleton

```text
Implement Phase 1 for forgeHQ.

Goal:
Create a no-op but valid staged pipeline with strict stage progression and fail-closed behavior.

Build:
- shaping run model
- stage router
- orchestrator skeleton
- worker interface contracts
- schema stubs for all core artifacts
- invalid transition protection

Required artifact schemas:
- shaping_run
- signal_snapshot
- target_ranking
- context_bundle
- candidate_design
- candidate_patch
- falsification_report
- candidate_verification
- confidence_shaping_summary
- forgehq_proposal

Hard rules:
- stages may not be skipped
- candidate generation is not allowed before candidate design exists
- proposal packaging is not allowed before falsification and verification artifacts exist
- fail closed on invalid parent refs, invalid transitions, or missing required artifacts

Add tests for:
- valid no-op progression through all stages
- invalid stage skip rejection
- generation-before-design rejection
- packaging-before-challenge rejection
- packaging-before-verification rejection

Do not add adapter-specific logic yet.
```

---

### Prompt 3 — Phase 2 Ranking and Context Slice

```text
Implement Phase 2 for forgeHQ.

Goal:
Allow forgeHQ to intake admitted signals, rank one target, and build one bounded context bundle.

Build:
- signal intake service
- source admissibility validation
- authority posture classification
- target ranking service
- ranking factor trace artifact
- context bundle builder
- source-ref validation
- scope boundary enforcement

Hard rules:
- deterministic evidence must remain separate from proposal interpretation
- context bundle must remain bounded to one target
- unresolved or semantically unknown inputs must fail closed
- if context scope exceeds policy, emit a blocked or degraded posture rather than expanding scope

Add tests for:
- invalid source rejection
- valid source-ref preservation
- bounded single-target context creation
- scope escape rejection
- ranking trace explainability presence

Do not implement candidate generation yet.
```

---

### Prompt 4 — Phase 3 Design and Generation Slice

```text
Implement Phase 3 for forgeHQ.

Goal:
Enforce design-before-generation and create bounded candidate patch artifacts.

Build:
- candidate design service
- design validators
- generator service contract
- DataForge-first adapter entry boundary
- out-of-scope rejection logic
- candidate patch artifact creation

Candidate design must include:
- bounded change hypothesis
- intended confidence gain
- targeted behaviors or contracts
- oracle strategy
- disconfirming checks
- failure hypotheses

Hard rules:
- no generation without valid design
- generation must remain inside scope boundary from context bundle and design
- preserve parent refs to ranking and context artifacts
- reject out-of-scope expansion

Add tests for:
- generation blocked without design
- generation blocked when design scope exceeds context scope
- valid candidate patch creation from valid design

Do not implement falsification or verification yet.
```

---

### Prompt 5 — Phase 4 Critic and Verification Slice

```text
Implement Phase 4 for forgeHQ.

Goal:
Make candidate proposals challengeable and measurable before review.

Build:
- falsification service
- contradiction checks
- duplicate-test detection hooks
- shallow-gain detection hooks
- downgrade logic
- candidate verification service
- gain and limitation recording
- fail-closed handling when measurement basis is missing

Hard rules:
- every candidate must receive an independent challenge artifact
- verification must show both observed gain and residual weakness
- no green-only posture is allowed
- missing measurement basis must fail closed

Add tests for:
- weak candidate downgrade
- contradiction recording
- verification includes gain and limitation
- missing measurement basis rejection

Do not implement final proposal packaging yet.
```

---

### Prompt 6 — Phase 5 Proposal Packaging and Persistence Slice

```text
Implement Phase 5 for forgeHQ.

Goal:
Assemble a complete proposal package and persist its lineage through DataForge-facing persistence boundaries.

Build:
- confidence shaping summary builder
- forgehq proposal artifact builder
- optional evidence bundle builder
- artifact registry persistence wiring
- lineage edge persistence
- proposal repository
- reviewability state computation

Hard rules:
- proposal is not reviewable unless design, candidate, challenge, verification, parent refs, and non-authoritative notice are all present
- proposal lifecycle state must remain separate from operator decision state
- missing backbone artifacts force not_reviewable
- preserve deterministic evidence lineage separately from proposal lineage

Add tests for:
- full backbone persistence
- not_reviewable on missing artifact
- lifecycle and decision separation
- lineage edge preservation

Do not implement ForgeCommand UI in this slice.
```

---

### Prompt 7 — Phase 6 ForgeCommand Integration Slice

```text
Implement Phase 6 for forgeHQ.

Goal:
Expose read models for ForgeCommand review surfaces.

Build:
- queue read model
- detail read model
- layered evidence/rationale/challenge/risk separation
- action-state support
- blocked-approval guard for non-reviewable proposals

Hard rules:
- do not flatten scores into misleading global summaries
- preserve layered proposal posture
- reviewability state must be explicit
- approval actions must be blocked when proposal is not reviewable

Add tests for:
- detail read model shape
- queue read model shape
- non-reviewable approval block
- layered evidence/challenge/risk rendering support
```

---

## 16. Repo-Level Codex Guidance File

Create a repo guidance file early with this intent:

### `AGENTS.md` recommended content areas
- system role and non-goals
- upstream/downstream boundaries
- artifact family map
- stage sequencing rules
- reviewability rules
- fail-closed requirements
- language posture rules
- coding standards for bounded implementation
- testing expectations per slice

This file should function as the standing operating doctrine for Codex inside the repo.

---

## 17. Recommended First Acceptance Target

The first real proof for forgeHQ is this minimum vertical slice:

1. shaping run model
2. target ranking artifact
3. context bundle artifact
4. candidate design artifact
5. candidate patch artifact
6. falsification report artifact
7. candidate verification artifact
8. final proposal artifact
9. DataForge persistence wiring
10. one ForgeCommand detail render path

If that slice works with tests and strict fail-closed posture, forgeHQ is no longer just a concept.

---

## 18. Final Build Direction

forgeHQ should be treated as a **hard implementation program**.

- ForgeEval remains deterministic evidence substrate
- ForgeMath remains governed mathematical authority where adopted
- forgeHQ becomes the bounded proposal-generation and confidence-shaping subsystem
- DataForge preserves lineage and persistence truth
- ForgeCommand remains the human review surface

That is the implementation-safe posture for VSCode Codex.

