# BDS Repo Audit Execution Protocol

**Date:** April 2, 2026  
**Time Zone:** America/New_York

## Intended destination

`01-company-core/ai-assisted-operations/`

## Protocol purpose

This protocol defines how BDS conducts a full-repository audit using AI in a way that is evidence-bound, architecture-aware, governance-aware, and usable in a single-operator environment.

This is not a code-style review protocol.
This is not a generic quality scan.
This is not a shallow prompt template.

It is the protocol for auditing a repository as a governed system with:

- identity
- boundaries
- contracts
- state
- execution flows
- deterministic logic where applicable
- testing posture
- documentation truth
- operational burden
- expansion readiness

---

## Protocol scope

Use this protocol when auditing any BDS repository that has real implementation, architectural boundaries, contracts, operational truth, or governance significance.

This includes, as applicable:

- backend/service repos
- local authority systems
- desktop applications with governed backend or authority posture
- infrastructure/control repos
- evaluation or testing subsystems
- specialized internal systems that act as canonical or quasi-canonical authority surfaces

This protocol should be used for:

- initial repo maturity assessment
- phase-boundary readiness review
- hardening review before expansion
- post-implementation repo audit
- drift review between implementation and declared system truth
- operator-burden and re-entry-risk review

---

## Core doctrine

### 1. Audit the repo as a system

The repo must be reviewed as an operational system, not as a loose source tree.

The audit must examine:

- what the repo is trying to be
- what it actually is right now
- where those two align
- where they diverge
- what is explicit
- what is implied
- what is missing
- what is dangerous

### 2. Evidence over impression

No major audit finding should exist without a concrete evidence basis.

Major findings should be grounded in one or more of the following:

- code paths
- route handlers
- service boundaries
- DTOs and schemas
- migrations
- state models
- tests
- documentation modules
- system reference files
- configuration surfaces
- operational scripts

The audit must not rely on tone, style, or vibes as a substitute for evidence.

### 3. Implemented truth must be separated from planned truth

The audit must distinguish clearly between:

- **implemented truth**
- **planned truth**
- **implied truth**
- **missing truth**

Deferred phases must not be graded as though they already exist.
Planned architecture must not be mistaken for current implementation.
Implemented limitations must not be hidden behind future intent.

### 4. Governance language must be tested against enforcement

If the repo claims:

- fail-closed posture
- immutable state rules
- contract discipline
- evidence separation
- deterministic behavior
- reviewability
- lifecycle enforcement
- authoritative truth posture

then the audit must check whether those claims are actually enforced in code, contracts, tests, or runtime behavior.

Governance language that exists only in prose must be identified as prose-only governance.

### 5. Single-operator reality is a first-class audit concern

Because BDS currently operates in a single-operator context, the audit must explicitly evaluate:

- re-entry difficulty
- maintenance burden
- hidden operator memory dependencies
- debugging friction
- complexity concentration
- unclear ownership zones
- places where safe maintenance depends on recall instead of structure

A repo that is theoretically strong but practically hard to re-enter safely must be scored accordingly.

---

## Truth-source hierarchy

When sources disagree, use this authority order unless repo-specific doctrine explicitly overrides it:

1. live code and enforced runtime behavior
2. tests and verification artifacts
3. schemas, DTOs, and contract definitions
4. migrations and persistence definitions
5. compiled system reference files such as `SYSTEM.md`
6. modular documentation source files
7. planning documents, prompts, and future-phase design material

### Interpretation rule

- Code without tests may show implementation but weak verification.
- Docs without code may show intent but not implemented truth.
- Plans may explain direction but must not be treated as current fact.

When a conflict exists, the audit must say so directly and classify the contradiction.

---

## Required audit lenses

Every full repo audit under this protocol must review the repository through the following lenses.

### 1. System identity and architectural coherence

Review:

- repo purpose
- system identity
- bounded responsibilities
- subsystem decomposition
- authority boundaries
- ownership lines
- whether the repo has one coherent identity or competing identities

Questions:

- What is this repo actually responsible for?
- What is it incorrectly trying to absorb?
- What belongs here and what does not?

### 2. Directory and codebase structure

Review:

- top-level layout
- folder logic
- module organization
- naming discipline
- separation of runtime, contracts, docs, tests, schemas, migrations, scripts, and projections
- signs of ad hoc growth

Questions:

- Is the structure helping safe maintenance?
- Where does the layout create drift or confusion?

### 3. Contract and schema discipline

Review:

- DTOs
- schemas
- payload boundaries
- request and response models
- enum governance
- compatibility posture
- fail-closed versus fail-open behavior
- separation between execution, evaluation, and projection surfaces

Questions:

- Which contracts are explicit?
- Which assumptions are unstated?
- Where are contract mismatches likely?

### 4. Data and state integrity

Review:

- persistence models
- canonical versus derived truth
- lifecycle handling
- lineage surfaces
- mutability boundaries
- invalidation
- supersession
- audit trails
- bundle consistency across related records

Questions:

- Where can state drift occur?
- Where can semantics be flattened incorrectly?
- Where can corruption or false consistency appear?

### 5. Runtime and execution flow

Review:

- orchestration flow
- runtime admission flow
- execution order
- composition order
- degraded-mode behavior
- error propagation
- blocking rules
- honesty of failure reporting

Questions:

- What are the real execution paths?
- What breaks first under stress?
- Are failures surfaced truthfully?

### 6. Math and deterministic execution discipline

Use this lens when the repo includes governed computation, scoring, banding, factor weighting, routing logic, or deterministic execution.

Review:

- formulas versus governing docs
- extraction and normalization order
- weighting stability
- trace sufficiency
- classification derivation
- rerun determinism
- expansion drift risk

Questions:

- Is the math actually governed?
- Which formulas are under-proven?
- What is likely to drift as the system expands?

### 7. Testing and verification posture

Review:

- unit tests
- integration tests
- contract tests
- schema tests
- lifecycle tests
- fail-closed tests
- degraded-mode tests
- runtime-admission tests
- determinism tests where relevant

Questions:

- What is truly well covered?
- What is only happy-path covered?
- What is high-risk and under-tested?
- Where do tests create a false sense of health?

### 8. Documentation truthfulness

Review:

- compiled system files
- modular documentation source
- README and onboarding docs
- architecture docs
- maintenance docs
- truth-policy posture
- stale or aspirational documentation

Questions:

- Which docs reflect real implementation?
- Which are stale or misleading?
- Where does the repo rely on tribal knowledge?

### 9. Governance and operational discipline

Review:

- naming discipline
- versioning discipline
- change control alignment
- schema evolution posture
- reviewability
- auditability
- evidence versus interpretation separation
- enforcement of claimed governance rules

Questions:

- Which governance rules are real?
- Which exist only in prose?
- What would break as the repo grows?

### 10. Security, safety, and boundary risk

Review:

- unsafe defaults
- missing validation
- hidden authority transfer
- accidental destructive paths
- environment/config fragility
- silent failure risk
- boundary leakage
- future production risk under expansion

Questions:

- What are the top safety risks?
- What could silently fail dangerously?
- Which risks get worse when scope expands?

### 11. Maintainability and operator burden

Review:

- clarity of re-entry
- operational burden
- debugging cost
- hidden dependency chains
- context reconstruction difficulty
- fragile workflows
- maintenance traps

Questions:

- How hard is safe upkeep?
- What most reduces operator burden?
- Where is the next maintenance trap likely?

---

## Required evidence standard

Every major audit finding should identify the evidence basis in plain language.

Recommended evidence tags:

- `code`
- `test`
- `contract`
- `schema`
- `migration`
- `route`
- `state model`
- `runtime path`
- `documentation`
- `config`
- `script`

The audit does not need to become unreadable with excessive quoting, but it must be obvious where each major judgment came from.

### Required rule

High-severity findings must be evidence-anchored.

If the auditor cannot identify evidence, the issue should be labeled as one of:

- probable risk
- inferred risk
- unverified concern

and must not be stated as established fact.

---

## Required weakness classification

Weaknesses identified by the audit must be classified as one or more of the following:

- **architecture**
- **boundary**
- **contract**
- **data/state**
- **execution**
- **test/verification**
- **documentation**
- **governance**
- **security/safety**
- **maintainability**

### Severity posture

Each major weakness should also be understood as:

- **structural** — threatens system shape or long-term governability
- **operational** — threatens safe use, execution, or maintenance
- **cosmetic** — readability or presentation issue without major system risk

The audit must avoid vague language such as “could be improved” when a weakness is clearly structural or operational.

---

## Expansion-readiness gate

Every full repo audit must end with an explicit expansion-readiness judgment.

Allowed verdicts:

### 1. Ready for expansion

Use only when:

- repo identity is coherent
- high-risk boundaries are governed
- core contracts are explicit
- state and execution behavior are sufficiently proven
- testing is materially credible for the next phase
- documentation is close enough to reality to support safe expansion

### 2. Ready only after bounded hardening

Use when:

- the core architecture is sound
- the next phase is plausible
- but specific structural, testing, contract, execution, or documentation weaknesses must be corrected first

This is the expected verdict for many promising but not yet expansion-safe repos.

### 3. Not ready for expansion

Use when:

- repo identity is drifting
- boundaries are blurred
- major contracts are implied rather than explicit
- state or execution posture is fragile
- tests materially overstate health
- docs meaningfully misrepresent implementation

This verdict should be blunt and specific.

---

## Standard audit execution sequence

When this protocol is used, the audit should generally proceed in this order:

1. establish repo identity and intended role
2. identify implemented phase truth
3. identify deferred or planned truth
4. inspect top-level structure and subsystem ownership
5. inspect contracts, schemas, DTOs, and state definitions
6. inspect execution flows and admission or gating logic
7. inspect deterministic logic or math surfaces where applicable
8. inspect tests and verification posture
9. inspect documentation truth and drift
10. inspect governance enforcement versus prose-only governance
11. inspect operator burden and re-entry risk
12. produce prioritized corrective actions
13. produce execution order
14. issue final expansion-readiness verdict

---

## Required deliverable structure

The audit output produced under this protocol should use the following structure:

# Entire Repo Audit

## 1. Executive assessment

State clearly whether the repo is:

- structurally strong
- promising but drifting
- functional but fragile
- architecturally at risk

## 2. What the repo is trying to be

State the repo’s actual system identity based on code and docs.

## 3. What is working well

List real strengths only.

## 4. What is weak, drifting, or dangerous

List highest-risk weaknesses.

## 5. Boundary violations or architecture drift

Identify blurred ownership or responsibility leakage.

## 6. Contract, schema, state, and execution risks

Identify major explicit and implicit failure surfaces.

## 7. Testing reality

State:

- what is actually well covered
- what is weakly covered
- what needs immediate test attention

## 8. Documentation truth review

State which docs reflect reality and which need correction.

## 9. Highest-priority corrective actions

Provide the top 10 actions in priority order.
Each must include:

- title
- why it matters
- what it fixes
- priority (`critical`, `high`, `medium`)
- work type (`architecture`, `code`, `test`, `contract`, `data`, `execution`, `documentation`, `governance`)

## 10. Suggested execution order

Provide a practical correction sequence.

## 11. Final verdict

End with one explicit judgment:

- ready for expansion
- ready only after bounded hardening
- not ready for expansion

Explain why.

---

## Anti-handwave rule

Audits under this protocol must not hide behind weak language.

Avoid:

- “might be improved”
- “could benefit from”
- “some concerns exist”
- “appears somewhat unclear”

Prefer:

- “this boundary is blurred because…”
- “this contract is implied rather than explicit because…”
- “this test posture overstates safety because…”
- “this documentation is stale because it claims X while implementation shows Y”

Directness is required because the point of the audit is correction, not comfort.

---

## Protocol maintenance rule

This protocol should be updated when one of the following changes materially:

- BDS repo governance posture
- documentation truth hierarchy
- audit evidence requirements
- phase-gate standards
- single-operator maintenance doctrine
- expected audit deliverable structure

When updated, the protocol revision should preserve:

- evidence-first posture
- implemented-versus-planned separation
- governance-versus-enforcement distinction
- single-operator maintainability as a core audit lens

---

## Final protocol law

**A BDS full-repository audit is valid only when it evaluates the repository as a governed operational system, grounds major judgments in evidence, distinguishes implemented truth from planned truth, tests governance claims against enforcement, and ends with a blunt expansion-readiness verdict.**

