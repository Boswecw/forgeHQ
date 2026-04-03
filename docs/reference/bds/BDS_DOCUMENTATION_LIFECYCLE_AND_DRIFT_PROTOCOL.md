# BDS Documentation Lifecycle and Drift Protocol

> Canonical doctrine for documentation lifecycle operations, drift detection, reconciliation, local-first documentation intelligence, and ForgeCommand-facing documentation truth consumption across BDS systems.

**Document class:** BDS company-core protocol  
**Status:** Canonical draft  
**Version:** 1.0  
**Date:** April 2, 2026  
**Time:** 12:22 PM America/New_York  
**Scope:** Company-core documentation lifecycle and drift doctrine  
**Recommended location:** `01-company-core/documentation-operations/BDS_DOCUMENTATION_LIFECYCLE_AND_DRIFT_PROTOCOL.md`

---

## 1. Purpose

This protocol defines how BDS systems should create, assemble, reconcile, monitor, consume, and govern documentation as a living control surface rather than a loose body of notes.

It is not a generic writing standard.
It is a doctrine and operations document for making sure documentation across BDS systems remains:

- canonical where it should be canonical
- explicitly snapshot-labeled where it is measured
- structurally assembled
- locally inspectable
- drift-aware
- reviewable
- consumable by operator tooling
- resistant to silent divergence from implementation reality

This protocol exists to prevent:

- documentation being treated as optional after code changes
- compiled system files being mistaken for hand-edited truth
- drift between code and system docs going unnoticed
- snapshot claims being mistaken for doctrine
- model-generated prose silently becoming canonical truth
- documentation tooling becoming a hidden authority layer
- HUD/Q&A surfaces answering from stale or ungrounded material

This protocol inherits from the architecture and systems design doctrine and remains aligned with backend, UX/UI, security, testing, release/change-control, and documentation protocol posture.

---

## 2. Executive doctrine

### 2.1 Documentation is a control surface

For BDS systems, documentation is part of operational governance.
It helps define:

- what a system is
- what it owns
- what it depends on
- what it exposes
- what it must not do
- what is canonical doctrine
- what is current measured state

### 2.2 The documentation assembly system remains canonical

Per real system or repo, the canonical documentation substrate is the modular assembly surface:

- `doc/system/`
- `_index.md`
- `BUILD.sh`
- compiled `{prefix}SYSTEM.md`

Module source files are the editable truth surface.
Compiled output is generated truth output, not the primary hand-edit surface.

### 2.3 Drift is a first-class signal

Documentation drift is not cosmetic staleness.
It is a diagnostics, analytics, review, and operator-support signal.

### 2.4 Documentation lifecycle tooling may assist, not silently govern

Lifecycle tooling may scaffold, inspect, compare, classify, and propose.
It must not silently redefine canonical truth or replace governed review for higher-order doctrine statements.

---

## 3. What this protocol governs

This protocol governs documentation lifecycle and drift operations for:

- backend/service repos
- desktop applications
- web applications
- public websites with real operational behavior
- internal workbench and authority systems
- specialty systems
- ecosystem/root documentation layers
- documentation intelligence subsystems
- ForgeCommand documentation ingestion and HUD support surfaces

This protocol applies wherever a real system has:

- implementation
- boundaries
- interfaces
- runtime behavior
- operational truth
- a need for canonical system documentation

---

## 4. Canonical documentation substrate doctrine

### 4.1 Every real system should have a documentation assembly system

The default documentation posture for a real system is a modular documentation assembly surface with:

- `doc/system/`
- `_index.md`
- `BUILD.sh`
- `doc/{prefix}SYSTEM.md`

This posture is the standard documentation assembly pattern across the ecosystem.

### 4.2 Module source is edited directly

The editable source of truth lives in modular files inside `doc/system/`.
The compiled system reference is rebuilt from those modules.

### 4.3 Compiled output is authoritative as output, not as source

The compiled `{prefix}SYSTEM.md` is the readable top-layer system reference.
It should not become the normal hand-edit surface because that collapses the assembly model.

### 4.4 Assembly contract must be explicit

Each documentation system should clearly state:

- input location
- assembly script
- output file
- ordering rule
- generated status note

---

## 5. Documentation truth-class doctrine

### 5.1 Canonical facts and snapshot facts must remain distinct

Documentation should explicitly distinguish between:

- canonical facts
- snapshot facts

Canonical facts define stable, architecture-shaping truth.
Snapshot facts record measured current counts or current audited conditions.

### 5.2 Canonical facts

Examples include:

- subsystem role
- ownership boundaries
- trust boundaries
- fail-closed doctrine
- lifecycle rules
- durable truth ownership
- HTTP vs CLI boundaries
- stable stage ordering where doctrinally fixed

### 5.3 Snapshot facts

Examples include:

- endpoint totals
- route counts
- component counts
- table counts
- test totals
- coverage percentages
- current file tallies

### 5.4 Snapshot claims must be visibly labeled

Use wording such as:

- current audited snapshot
- current code snapshot
- audit-derived count
- as of this document version

Do not present volatile counts as timeless doctrine.

---

## 6. Documentation lifecycle doctrine

Documentation lifecycle operations should be understood as three major jobs.

### 6.1 Birth / scaffolding

When a new real system is admitted, the documentation lifecycle should be able to:

- detect or admit the system
- assign or confirm documentation identity
- scaffold the documentation assembly structure
- generate a first-pass system story where appropriate
- assemble the first compiled system reference

### 6.2 Reconciliation / drift

For an existing system, the lifecycle should be able to:

- inspect implementation reality
- inspect modular documentation
- inspect compiled documentation
- compare them in both directions
- detect and classify drift
- emit findings and candidate proposals

### 6.3 Consumption / operator support

For operator-facing tooling, the lifecycle should make it possible to:

- answer questions from canonical docs
- show documentation health
- show drift posture
- provide evidence-backed issue explanations
- support review and proposal handling inside ForgeCommand/HUD

This three-job model is the correct high-level frame for the documentation lifecycle node.

---

## 7. Local-first documentation lifecycle doctrine

### 7.1 Initial implementation is local-first

The documentation lifecycle node should be designed to operate meaningfully on the local machine.

That includes:

- local code inspection
- local filesystem access
- local documentation assembly
- local drift analysis
- local indexing/retrieval
- local model inference where needed
- local persistence or local-first writeback posture

### 7.2 No cloud dependency for initial production posture

The initial documentation lifecycle architecture must not depend on cloud inference in order to be useful.

### 7.3 Single-operator optimization matters

Because the working posture is single-operator and terminal-driven, the lifecycle should optimize for:

- many systems
- repeated context switching
- trustworthy recall
- low tolerance for invisible complexity
- fast operator comprehension

---

## 8. Documentation lifecycle node responsibilities

The documentation lifecycle node should own these bounded responsibilities.

### 8.1 System birth admission

Determine when a repo or system should gain a documentation assembly surface.

### 8.2 Scaffold generation

Create or repair:

- `doc/system/`
- `_index.md`
- `BUILD.sh`
- baseline module set
- compiled `{prefix}SYSTEM.md`

### 8.3 Structural extraction

Collect implementation evidence such as:

- project structure
- routes
- commands
- config/env surfaces
- integration points
- persistence surfaces
- test surfaces
- schema inventories

### 8.4 Reconciliation

Compare:

- code vs modular docs
- modular docs vs compiled docs
- compiled docs vs implementation evidence
- docs vs protocol expectations

### 8.5 Drift classification

Emit structured drift classes and severity/trace posture.

### 8.6 Truth packaging for consumers

Prepare outputs for ForgeCommand, HUD, and other operator surfaces such as:

- documentation health summaries
- drift findings
- cited canonical sections
- explanation summaries
- candidate proposals
- Q&A retrieval packages

These responsibilities reflect the right boundary for the lifecycle node as an engine rather than a manual authoring surface.

---

## 9. Drift doctrine

### 9.1 Drift is a diagnostics class

Drift between implementation and canonical documentation should be treated as:

- diagnostics
- analytics
- review input
- operator visibility material

not just stale markdown.

### 9.2 Drift families should be explicit

Example drift classes include:

- `missing_doc_system`
- `assembly_missing`
- `compiled_stale`
- `protocol_noncompliance`
- `implementation_ahead_of_docs`
- `docs_ahead_of_implementation`
- `snapshot_stale`
- `canonical_boundary_mismatch`
- `unresolved_inference_gap`

### 9.3 Drift should preserve evidence posture

A drift finding should identify:

- drift class
- severity
- confidence
- canonical section references
- implementation evidence references
- recommended next action
- history where repeated

### 9.4 Drift does not automatically authorize rewrite

A detected mismatch does not automatically permit silent modification of doctrine-level documentation.
It creates a review signal, not an autonomous truth rewrite.

---

## 10. Deterministic vs model-assisted work doctrine

### 10.1 Deterministic tasks should stay deterministic

The lifecycle should prefer deterministic methods for tasks such as:

- folder detection
- module presence checks
- `BUILD.sh` existence
- compiled output staleness checks
- route enumeration where machine-readable
- config discovery
- schema inventory
- structure inventory

### 10.2 Model-assisted tasks should remain bounded

Model assistance may be used for:

- first-pass system story drafting
- converting structural evidence into readable prose
- summarizing drift meaning for the operator
- proposing candidate updates to higher-order sections
- explaining documentation issues in HUD language
- answering questions from bounded retrieved context

### 10.3 Retrieval-before-generation is mandatory

Model-assisted work must follow this pattern:

1. collect deterministic signals
2. retrieve canonical documentation sections
3. retrieve relevant structural/code evidence
4. identify truth class
5. pass bounded evidence package to the model
6. produce answer, draft, or proposal from that evidence only

This is required to keep generation grounded rather than freeform.

### 10.4 Model output is proposal or support, not silent doctrine

A local model may draft, explain, compare, and summarize.
It may not silently define canonical truth, invent architecture facts, or rewrite approved doctrine without governed adoption.

---

## 11. Auto-generation vs review-required doctrine

### 11.1 Safe-to-auto-generate surfaces

The following are generally eligible for deterministic generation or update:

- `_index.md`
- `BUILD.sh`
- deterministic inventory sections
- route listings
- command listings
- config variable listings
- schema inventories
- project structure sections
- measured snapshot facts
- compiled system file rebuilds from approved module source

### 11.2 Review-required surfaces

The following should be drafted or proposed, not silently canonicalized:

- system role
- architecture doctrine
- ownership boundaries
- authority boundaries
- fail-closed philosophy
- governance language
- security claims
- statements about what the system is and is not

This is a critical control boundary for the documentation lifecycle system.

---

## 12. ForgeCommand ingestion doctrine

### 12.1 ForgeCommand consumes derived read models

ForgeCommand should not consume raw internal pipeline fragments from documentation lifecycle processing.
It should consume explicit read models.

### 12.2 Core read-model families

Recommended read models include:

- documentation fleet summary
- documentation system detail
- drift finding detail
- HUD Q&A read model

### 12.3 Documentation fleet summary

Per system, this should be able to provide:

- system id
- prefix
- family
- doc system present/missing
- assembly status
- last build status
- drift posture
- open issue count
- last drift-check time

### 12.4 Documentation system detail

For one system, this should be able to provide:

- canonical doc status
- module inventory
- compiled file status
- protocol compliance status
- current drift findings
- cited relevant sections
- latest proposed updates

### 12.5 Drift finding detail

For one issue, this should be able to provide:

- drift id
- class
- severity
- confidence
- evidence bundle
- canonical references
- implementation evidence references
- recommended next action
- history if repeated

---

## 13. HUD documentation-truth-library doctrine

### 13.1 HUD should use docs as a truth library

Inside ForgeCommand, HUD should not act as a generic chatbot over stale text.
It should answer against:

- canonical documentation sections
- structural evidence
- active drift findings where relevant

### 13.2 HUD answer requirements

HUD answers should:

- prefer canonical docs first
- include drift context when relevant
- identify truth class such as `canonical`, `snapshot`, `inferred`, or `missing_declared_truth`
- cite relevant sections
- avoid freeform guessing

### 13.3 HUD question classes

Representative question classes include:

- what does this subsystem do?
- what owns this boundary?
- why is this drift being reported?
- what changed compared with the documentation claim?
- is this issue structural, snapshot-only, or doctrinal?

This is the correct operator-support posture for documentation Q&A.

---

## 14. Persistence and analytics doctrine

### 14.1 Documentation lifecycle should persist meaningful events

Recommended persisted classes include:

- birth/scaffold events
- assembly results
- drift findings
- drift history
- issue lifecycle state
- proposal records
- review outcomes
- Q&A evidence packs where useful

### 14.2 Drift analytics are valuable

Drift should become an analytics lane with dimensions such as:

- drift count by system
- repeated drift classes
- stale compiled docs frequency
- missing doc-system events
- protocol noncompliance count
- unresolved doctrinal mismatches
- time to resolution

### 14.3 Persistence should remain local-first initially

Long-horizon history may later be written upstream into durable system-of-record layers, but the initial documentation lifecycle architecture can begin with local-first persistence.

---

## 15. Documentation update law

### 15.1 Structural implementation change requires documentation update

If implementation changes system behavior, interfaces, boundaries, structural truth, or canonical claims, related documentation modules must be updated before the work is considered complete.

### 15.2 Build output should be regenerated after source changes

After source-module updates, the compiled system file should be rebuilt using the deterministic assembly contract.

### 15.3 Reconciliation should respect current canonical doctrine

When two surfaces disagree, correction should follow truth class:

- correct stale snapshot facts
- update canonical facts only when architecture or doctrine really changed
- remove lower-value duplicates when they create contradiction

This matches the broader documentation truth policy.

---

## 16. Operator posture doctrine

### 16.1 ForgeCommand is not the manual authoring surface

ForgeCommand should be the place where documentation lifecycle work is:

- initiated
- observed
- reviewed
- questioned
- governed
- consumed as a truth library

It should not become the place where canonical documentation is casually authored directly.

### 16.2 Documentation lifecycle tooling should reduce memory burden

In a single-operator environment, the lifecycle system should reduce context-switching burden and improve trustworthy recall.

### 16.3 Documentation issue language should remain operationally useful

Drift and issue summaries should help the operator understand:

- what is wrong
- what class of truth is affected
- what evidence supports the finding
- what action is recommended next

---

## 17. Testing and verification doctrine for lifecycle systems

### 17.1 Documentation lifecycle systems require their own verification

Testing should cover:

- scaffold generation correctness
- assembly compliance
- compiled staleness detection
- drift classification behavior
- truth-class labeling
- read-model shape validity
- HUD evidence-grounding behavior
- deterministic-vs-model-assisted boundary enforcement

### 17.2 Drift detection should be tested against known scenarios

Important scenarios include:

- missing doc system
- stale compiled output
- implementation ahead of docs
- docs ahead of implementation
- canonical boundary mismatch
- snapshot-only staleness

### 17.3 Model assistance must be bounded in tests too

Tests should verify that model-assisted flows do not:

- invent unsupported canonical facts
- answer without retrieval context
- silently rewrite review-required surfaces

---

## 18. Release and change-control linkage

### 18.1 Documentation lifecycle changes can be structural changes

Changes to documentation lifecycle scaffolding, drift semantics, truth-class handling, or ForgeCommand ingestion shape may themselves be architecture-relevant changes.

### 18.2 Documentation lifecycle outputs affect release confidence

If documentation health or drift findings indicate unresolved mismatch on structural truth, that should influence release and change-control posture.

### 18.3 Completion language must remain truthful here too

Documentation lifecycle work should use truthful status labels such as:

- proposed
- scaffolded
- partially reconciled
- drift-detected
- review-required
- locally verified
- accepted with limitations

---

## 19. Anti-patterns BDS rejects

Reject these unless explicitly authorized by architecture review:

- hand-editing compiled `{prefix}SYSTEM.md` as the main truth surface
- presenting snapshot counts as timeless doctrine
- silent model-written doctrine updates
- treating documentation drift as merely cosmetic
- using HUD or Q&A without retrieved canonical grounding
- letting ForgeCommand become casual manual doc authoring space
- auto-canonicalizing security or architecture claims
- claiming a repo is documented because a compiled file exists while source modules are stale or structurally weak

---

## 20. Relationship to adjacent protocols

This protocol inherits from:

- BDS Architecture and Systems Design Protocol

This protocol should remain aligned with:

- BDS Documentation Protocol
- backend engineering doctrine
- frontend and UX/UI doctrine
- security and hardening doctrine
- testing and verification doctrine
- release and change-control doctrine
- AI-assisted development operations doctrine

---

## 21. Final doctrine statement

BDS documentation lifecycle and drift doctrine is governed by four persistent truths:

1. **The modular documentation assembly system remains the canonical substrate.**
2. **Canonical facts and snapshot facts must remain distinct.**
3. **Documentation drift is a first-class diagnostics and review signal.**
4. **Lifecycle tooling may assist and propose, but it must not silently redefine canonical truth.**

Any system that violates those rules may still produce documents, but it is not operating at BDS standard.
