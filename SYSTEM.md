# forgeHQ — Complete System Reference

> Bounded proposal-generation and confidence-shaping subsystem for the BDS ecosystem.
> "Reviewable candidates without counterfeit authority."

**Document version:** 1.2 (2026-04-03) — Phase 1 scaffold plus QA foundation

---

## Table of Contents

1. [Overview & Philosophy](#1-overview--philosophy)
2. [Architecture](#2-architecture)
3. [Tech Stack](#3-tech-stack)
4. [Project Structure](#4-project-structure)
5. [Configuration & Environment](#5-configuration--environment)
6. [Design System](#6-design-system)
7. [Frontend](#7-frontend)
8. [API Layer](#8-api-layer)
9. [Backend](#9-backend)
10. [Ecosystem Integration](#10-ecosystem-integration)
11. [Database Schema](#11-database-schema)
12. [AI Integration](#12-ai-integration)
13. [Proposal Artifact Model](#13-proposal-artifact-model)
14. [Pipeline & Reviewability](#14-pipeline--reviewability)
15. [Error Handling Contract](#15-error-handling-contract)
16. [Testing Infrastructure](#16-testing-infrastructure)
17. [Handover / Migration Notes](#17-handover--migration-notes)

---

## 1. Overview & Philosophy

forgeHQ is a backend/domain-contract repository for bounded proposal generation.
The current repo state implements the governance slice, the documentation stack,
and a Phase 1 no-op pipeline scaffold.
This repository defines how forgeHQ names artifacts, stages work,
separates proposal posture from decision posture,
and advances a shaping run through bounded placeholder artifacts without inventing live runtime semantics.

### 1.1 Core Principles

- forgeHQ is non-authoritative by design.
- Upstream truth remains with ForgeEval and ForgeMath where adopted.
- Human review remains downstream of forgeHQ proposals.
- Challenge and verification are mandatory before reviewability.
- Proposal lifecycle state never collapses into operator decision state.
- Ambiguity and scope escape fail closed.
- Documentation is part of repo truth, not a side artifact.

### 1.2 Current Product Boundary

| Area | Current status |
| --- | --- |
| Governance docs | Implemented |
| Artifact family registry | Implemented |
| Stage vocabulary | Implemented |
| Worker boundary registry | Implemented |
| Shaping run model | Implemented |
| Core artifact schema stubs | Implemented |
| Strict stage router | Implemented |
| No-op orchestrator skeleton | Implemented |
| Reviewability vocabulary | Implemented |
| Documentation assembly stack | Implemented |
| API surface | Not implemented |
| Live stage services | Not implemented |
| Persistence layer | Not implemented |
| Adapters and persistence wiring | Not implemented |
| UI or operator surface | Not implemented |

---

## 2. Architecture

The current implementation is a contract-first Python repository.
It still does not expose an application runtime,
but it now includes a no-op shaping-run scaffold that can progress through all stages with placeholder artifacts.
Repo architecture is centered on bounded domain contracts, typed schema stubs,
strict stage routing, and a documentation assembly surface.

### 2.1 Current Implemented Shape

```text
forgeHQ/
  app/domain/artifacts/
  app/domain/pipeline/
  app/domain/reviewability/
  app/domain/workers/
  app/schemas/
  app/orchestration/
  docs/architecture/
  docs/contracts/
  doc/system/
  scripts/
  tests/
```

### 2.2 Boundary Diagram

```text
ForgeEval / ForgeMath
        |
        v
   forgeHQ contracts
        |
        v
DataForge / ForgeCommand
```

### 2.3 Architectural Posture

| Concern | Current posture |
| --- | --- |
| Upstream authority | Declared boundary only |
| Runtime orchestration | Implemented as a no-op stage scaffold only |
| Persistence boundary | Declared boundary only |
| Operator review surface | Declared boundary only |
| Repo documentation truth | Implemented via `doc/system/` and `SYSTEM.md` |

### 2.4 Hard Architectural Laws

- forgeHQ may consume upstream evidence but may not overwrite upstream canonical truth
- no proposal becomes reviewable without challenge and verification
- orchestrator sequencing may exist later, but orchestrator proposal authorship is forbidden
- reviewability posture must stay explicit, not inferred

---

## 3. Tech Stack

The current repo uses a minimal stack because only the governance contract slice is implemented.

### 3.1 Runtime and Test Stack

| Layer | Current choice | Notes |
| --- | --- | --- |
| Language | Python 3.12 | Current local interpreter |
| Test framework | `pytest==7.4.3` | Repo contract tests |
| Shell scripting | Bash | Documentation assembly and context-bundle scripts |
| Docs format | Markdown | Canonical repo-reference format |

### 3.2 Python Standard Library Usage

| Module | Current use |
| --- | --- |
| `enum` | `StrEnum` vocabularies for bounded contracts |
| `dataclasses` | Frozen contract helpers |
| `types.MappingProxyType` | Immutable registry views |

### 3.3 Not Yet Present

| Category | Current status |
| --- | --- |
| Web framework | Not implemented |
| ORM/migrations | Not implemented |
| Database driver | Not implemented |
| Frontend framework | Not implemented |
| Runtime AI provider SDK | Not implemented |

---

## 4. Project Structure

The current repo structure is intentionally narrow.
It reflects a contract-first bootstrap rather than a full service implementation.

### 4.1 Directory Layout

```text
forgeHQ/
├── FORGEHQ_COMPREHENSIVE_TEST_PLAN.md
├── app/
│   ├── domain/
│   │   ├── artifacts/
│   │   ├── pipeline/
│   │   ├── reviewability/
│   │   └── workers/
│   ├── orchestration/
│   └── schemas/
├── doc/
│   └── system/
├── docs/
│   ├── architecture/
│   ├── audits/
│   ├── contracts/
│   ├── qa/
│   └── reference/bds/
├── scripts/
├── tests/
│   ├── contract/
│   ├── pipeline/
│   └── workers/
├── CLAUDE.md
├── SYSTEM.md
├── pytest.ini
└── requirements.txt
```

### 4.2 File Naming Rules

| Surface | Rule |
| --- | --- |
| Domain enums | `enums.py` inside bounded domain folders |
| Schema stubs | one artifact or run model per file under `app/schemas/` |
| Orchestration | router/orchestrator modules under `app/orchestration/` |
| Contract tests | `test_*.py` under `tests/contract/` or related slices |
| System docs | numbered files under `doc/system/` |
| Imported doctrine references | `docs/reference/bds/` |
| QA support docs | `docs/qa/` |
| Root system reference | generated `SYSTEM.md` |
| Root QA plan | `FORGEHQ_COMPREHENSIVE_TEST_PLAN.md` |
| Repo instructions | root `CLAUDE.md` |
| QA scripts | `scripts/qa-*.sh` |

### 4.3 Generated Files

| File | Generation source |
| --- | --- |
| `SYSTEM.md` | `doc/system/_index.md` plus numbered part files via `doc/system/BUILD.sh` |
| `context-bundle.md` | selected documentation sections via `scripts/context-bundle.sh` |

---

## 5. Configuration & Environment

The current repo does not define service-runtime environment variables because no service runtime is implemented yet.
One optional QA tooling override is supported for test-runner discovery.

### 5.1 Environment Variables

| Variable | Type | Default | Reader | Status |
| --- | --- | --- | --- | --- |
| `PYTEST_RUNNER` | path string | auto-detected | `scripts/qa-mode-a-preflight.sh`, `scripts/qa-regression-smoke.sh` | Optional override for the pytest executable |

### 5.2 Operational Commands

| Command | Purpose |
| --- | --- |
| `python3 -m pytest` | Run repo tests when `pytest` is installed locally |
| `doc/system/BUILD.sh` | Rebuild root `SYSTEM.md` |
| `scripts/context-bundle.sh --list` | Show selective doc-loading options |
| `scripts/qa-mode-a-preflight.sh` | Execute Mode A T0 QA checks for current repo maturity |
| `scripts/qa-regression-smoke.sh` | Run the lightweight regression smoke suite |

### 5.3 Configuration Posture

- Service runtime configuration is intentionally absent until a service slice exists.
- QA tooling may use `PYTEST_RUNNER` to pin a specific pytest executable while the repo remains environment-light.
- When service configuration appears later, every variable must be documented here with type, default, and owner.

---

## 6. Design System

forgeHQ currently has no user-facing frontend and therefore no UI design token system.
Its current design surface is documentation and contract language.

### 6.1 Documentation Style Rules

| Rule | Current posture |
| --- | --- |
| Voice | Present tense and declarative |
| Proposal posture | Explicitly non-authoritative |
| Structured data | Prefer tables for registries and contracts |
| Root truth surface | `doc/system/` plus generated `SYSTEM.md` |

### 6.2 Non-Authoritative Language

Allowed language includes:

- propose
- hypothesize
- suggest
- indicate
- candidate
- challenge

Prohibited language includes:

- approved
- confirmed fix
- proven truth
- must apply
- merge now

---

## 7. Frontend

forgeHQ currently implements no frontend surface.

### 7.1 Current Status

| Surface | Status |
| --- | --- |
| Browser UI | Not implemented |
| Desktop UI | Not implemented |
| Operator dashboard | Not implemented in this repo |

### 7.2 Boundary Note

Human review is a downstream concern intended for ForgeCommand-facing surfaces,
not a current frontend owned by this repository.

---

## 8. API Layer

forgeHQ currently exposes no HTTP or RPC API.

### 8.1 Current Status

| Surface | Status |
| --- | --- |
| HTTP routes | Not implemented |
| Request schemas | Not implemented |
| Auth middleware | Not implemented |
| Error response contracts | Not implemented |

### 8.2 Boundary Note

API surfaces may appear in later phases,
but no transport contract is part of the current repo truth.

---

## 9. Backend

The backend currently consists of domain-contract modules,
typed schema stubs, a strict stage router, and a no-op orchestrator.
No live service runtime or persistence layer has been implemented yet.

### 9.1 Current Backend Modules

| Module | Files | Current responsibility |
| --- | --- | --- |
| Artifact domain | `app/domain/artifacts/enums.py` | Artifact families, lineage layers, backbone registry |
| Pipeline domain | `app/domain/pipeline/enums.py` | Stage order, stage artifacts, stage owners |
| Reviewability domain | `app/domain/reviewability/enums.py` | Reviewability requirements, lifecycle state split, language posture |
| Worker domain | `app/domain/workers/enums.py` | Worker identities and allowed emissions |
| Schema stubs | `app/schemas/` | Typed placeholders for shaping runs and required artifacts |
| Stage router | `app/orchestration/stage_router.py` | Fail-closed stage-order and predecessor validation |
| No-op orchestrator | `app/orchestration/forgehq_orchestrator.py` | Placeholder artifact emission in strict stage order |

### 9.2 Current Missing Backend Slices

| Slice | Status |
| --- | --- |
| `app/services/` | Not implemented |
| `app/persistence/` | Not implemented |
| `app/read_models/` | Not implemented |

### 9.3 Backend Law

Current backend code exists to lock repo semantics before live service logic arrives.
The orchestrator is a bounded scaffold for placeholder progression, not production execution semantics.

---

## 10. Ecosystem Integration

forgeHQ exists inside a larger BDS ecosystem but currently ships only declared boundaries rather than live adapters.

### 10.1 Boundary Table

| System | Relationship | Current status |
| --- | --- | --- |
| ForgeEval | Upstream evidence substrate | Declared boundary only |
| ForgeMath | Upstream math/rule authority where adopted | Declared boundary only |
| DataForge | Downstream persistence, lineage, rollback linkage | Declared boundary only |
| ForgeCommand | Downstream review surface and operator action state | Declared boundary only |

### 10.2 Integration Laws

- forgeHQ may consume upstream artifacts but may not overwrite upstream truth
- forgeHQ proposals remain non-authoritative even after packaging
- operator action state belongs downstream and stays separate from proposal lifecycle state

---

## 11. Database Schema

forgeHQ currently defines no database schema.
No migrations, tables, or repository persistence models exist in the current repo state.

### 11.1 Current Persistence Status

| Surface | Status |
| --- | --- |
| SQL migrations | Not implemented |
| ORM models | Not implemented |
| Artifact registry tables | Not implemented |
| Lineage edge tables | Not implemented |
| Proposal rows | Not implemented |

### 11.2 Future Boundary

When persistence is added later, DataForge-facing lineage and proposal persistence must preserve:

- deterministic evidence lineage
- non-authoritative proposal lineage
- operator decision linkage

---

## 12. AI Integration

forgeHQ currently has no runtime AI inference surface.
AI usage is limited to AI-assisted software development against the repository documentation stack.

### 12.1 Current AI Surfaces

| Surface | Status |
| --- | --- |
| Runtime model invocation | Not implemented |
| Provider routing | Not implemented |
| Prompt persistence | Not implemented |
| Dev-time context loading | Implemented via `CLAUDE.md` and `scripts/context-bundle.sh` |

### 12.2 Current AI Governance

- repo truth is assembled through `doc/system/`
- root `CLAUDE.md` defines project-specific working rules
- context bundles select bounded documentation slices for implementation work
- generated model output does not become canonical upstream truth by itself

---

## 13. Proposal Artifact Model

forgeHQ artifact vocabulary is implemented as explicit enum-backed families.
Every current artifact family is non-authoritative by posture,
and Phase 1 schema stubs provide typed placeholder models for the required artifact set.

### 13.1 Artifact Families

| Artifact family | Required for reviewability backbone | Purpose |
| --- | --- | --- |
| `signal_snapshot` | yes | admitted source signals and source refs |
| `intake_diagnostics` | no | signal-intake diagnostics |
| `target_ranking` | yes | governed improvement-target ranking |
| `ranking_factor_trace` | no | explainability trace for ranking factors |
| `context_bundle` | yes | bounded single-target context |
| `candidate_design` | yes | bounded change hypothesis |
| `candidate_patch` | yes | generated candidate change |
| `falsification_report` | yes | independent challenge artifact |
| `candidate_verification` | yes | observed gain and residual weakness |
| `confidence_shaping_summary` | yes | non-authoritative confidence summary |
| `forgehq_proposal` | yes | human-review package |
| `forgehq_evidence_bundle` | no | optional supporting evidence bundle |

### 13.2 Lineage Layers

| Layer | Meaning |
| --- | --- |
| `deterministic_evidence` | upstream evidence lineage |
| `non_authoritative_proposal` | forgeHQ proposal lineage |
| `operator_decision` | downstream human decision lineage |

### 13.3 Artifact Law

Missing any required backbone artifact forces `not_reviewable`.

---

## 14. Pipeline & Reviewability

The current repo implements the vocabulary for the shaping pipeline and reviewability gates,
plus a Phase 1 no-op router/orchestrator that can advance a shaping run with placeholder artifacts.
It still does not implement the live services behind those stages.

### 14.1 Stage Order

| Order | Stage | Primary owner |
| --- | --- | --- |
| 1 | `signal_intake` | `signal_analyst` |
| 2 | `target_ranking` | `signal_analyst` |
| 3 | `context_curation` | `context_curator` |
| 4 | `candidate_design` | `designer` |
| 5 | `candidate_generation` | `generator` |
| 6 | `falsification` | `critic_falsifier` |
| 7 | `verification` | `verifier` |
| 8 | `proposal_packaging` | `proposal_assembler` |

### 14.2 Reviewability Conditions

A proposal is reviewable only when all of the following are present:

- design
- candidate
- challenge
- verification
- non-authoritative notice
- explicit scope boundary statement
- valid parent refs
- no unresolved scope escape
- no broken lineage condition

### 14.3 Automatic Not-Reviewable Conditions

- missing challenge artifact
- missing verification artifact
- missing source refs
- scope escape detected
- invalid parent evidence refs
- confidence summary missing downgrade factors
- rollback class required but absent

### 14.4 Worker Boundary Law

- each worker emits only its admitted artifact families
- orchestrator emits no proposal content
- generator and critic/falsifier lanes remain structurally independent

### 14.5 Phase 1 Router Guarantees

- no stages may be skipped
- candidate generation is blocked when candidate design is missing
- proposal packaging is blocked when falsification is missing
- proposal packaging is blocked when verification is missing
- invalid run histories fail closed before artifact emission

---

## 15. Error Handling Contract

Current repo behavior is fail-closed by doctrine.
The implemented contract layer treats missing truth, collapsed states,
and invalid boundary assumptions as hard failures, not recoverable guesses.

### 15.1 Current Fail-Closed Conditions

| Condition | Current contract posture |
| --- | --- |
| Ambiguous system role | Reject broadening repo authority |
| Missing challenge or verification for reviewability | `not_reviewable` |
| Proposal/operator state collapse | Forbidden by separate enums |
| Missing documentation build inputs | Build and context scripts exit non-zero |
| Unknown preset or section in context bundle | Script exits non-zero |

### 15.2 Current Error Surface

| Surface | Current handling |
| --- | --- |
| Python contract violations | Test-detected invariant failure |
| Bash documentation scripts | Non-zero exit with stderr message |
| Runtime API errors | Not applicable because no API exists |

---

## 16. Testing Infrastructure

The current repo now includes a QA protocol foundation sized to actual maturity.
forgeHQ remains a contract/bootstrap repo with a Phase 1 scaffold,
so testing is centered on T0 pre-flight, T1 contract coverage, and limited T6 tooling checks.

### 16.1 QA Foundation Artifacts

| Surface | Responsibility |
| --- | --- |
| `FORGEHQ_COMPREHENSIVE_TEST_PLAN.md` | spec-first test plan derived from current `SYSTEM.md` truth |
| `docs/qa/FORGEHQ_MODE_A_T0_CHECKLIST.md` | human-readable Mode A pre-flight checklist |
| `docs/qa/FORGEHQ_QA_FINDINGS_LOG_TEMPLATE.md` | findings capture template using BugCheck-style severity levels |
| `docs/qa/FORGEHQ_QA_RUN_REPORT_TEMPLATE.md` | run-report template for applicable tiers |
| `docs/qa/FORGEHQ_TIER_APPLICABILITY_MATRIX.md` | explicit T0-T8 applicability and defer rationale |
| `scripts/qa-mode-a-preflight.sh` | executable T0 checks for the current repo |
| `scripts/qa-regression-smoke.sh` | lightweight regression smoke suite |

### 16.2 Current Test Suites

| Test file | Coverage |
| --- | --- |
| `tests/contract/test_artifact_schemas.py` | non-authoritative schema defaults and shaping-run lifecycle posture |
| `tests/contract/test_governance_enums.py` | artifact families, pipeline order, language posture, lifecycle-state separation |
| `tests/workers/test_worker_emission_boundaries.py` | worker registry coverage and generator/critic separation |
| `tests/contract/test_documentation_protocol.py` | required documentation surfaces, system build parity, context-bundle behavior |
| `tests/contract/test_qa_protocol_foundation.py` | QA plan, templates, applicability matrix, and script exposure |
| `tests/pipeline/test_stage_progression.py` | valid no-op stage progression and skip rejection |
| `tests/pipeline/test_design_required_before_generation.py` | candidate-generation block when design is missing |
| `tests/pipeline/test_reviewability_requires_challenge_and_verification.py` | packaging blocks when falsification or verification are missing |

### 16.3 Current Test Commands

| Command | Purpose |
| --- | --- |
| `python3 -m pytest` | Standard repo test run when local `pytest` is available |
| `doc/system/BUILD.sh` | Rebuild and verify root `SYSTEM.md` |
| `scripts/context-bundle.sh --dry-run --preset core --with-roadmap` | Verify selective context assembly inputs |
| `scripts/qa-mode-a-preflight.sh` | Run Mode A T0 checks for current repo maturity |
| `scripts/qa-regression-smoke.sh` | Run the lightweight regression smoke suite |

### 16.4 Tier Applicability

| Tier | Status | Current rationale |
| --- | --- | --- |
| T0 | Applicable now | docs build, context loading, pytest discovery, and repo tests are real current surfaces |
| T1 | Applicable now | governance, documentation, worker, schema, orchestration, and QA contracts exist |
| T2 | Not applicable yet | no UI surface exists |
| T3 | Not applicable yet | no API surface exists |
| T4/T5 | Not applicable yet | no live runtime or multi-module end-to-end flow exists |
| T6 | Limited applicability now | only tooling responsiveness is measurable today |
| T7 | Not applicable yet | no packaging or release target exists |
| T8 | Not applicable yet | no UI surface exists |

### 16.5 Test Posture

- contract and pipeline tests remain mandatory because repo semantics are contract-first
- documentation build parity remains a testable invariant
- Mode A T0 is the required QA entry gate for the current repo maturity
- regression smoke coverage is intentionally narrow and focuses on documentation plus stage-order regressions
- new repo truth requires matching documentation, QA-plan, and test updates in the same change

---

## 17. Handover / Migration Notes

The current repo is a Phase 1 baseline.
It now includes a no-op shaping pipeline skeleton,
but it should not be misread as a functional shaping service yet.

### 17.1 Current Handover Summary

| Topic | Current truth |
| --- | --- |
| Repo maturity | Governance baseline plus Phase 1 stage scaffold |
| Runtime capability | No-op stage progression with placeholder artifacts only |
| Canonical documentation source | `doc/system/` |
| Root build artifact | `SYSTEM.md` |
| Root QA plan | `FORGEHQ_COMPREHENSIVE_TEST_PLAN.md` |
| QA support docs | `docs/qa/` |
| QA executable entrypoints | `scripts/qa-mode-a-preflight.sh`, `scripts/qa-regression-smoke.sh` |
| Selective context source | `scripts/context-bundle.sh` |
| Imported ecosystem doctrine | `docs/reference/bds/` |

### 17.2 Migration Notes

- existing governance docs in `docs/` remain valid source material and are now reflected in the assembled system reference
- company-core protocols are stored as imported references under `docs/reference/bds/`, not as ambiguous repo-root files
- QA protocol compliance for current maturity now lives in the root test plan plus `docs/qa/` support artifacts
- future service slices must update both `docs/` and `doc/system/` when repo truth changes
- repo-local Phase 1 implementation and QA foundation are complete enough to support bounded Phase 2 work
