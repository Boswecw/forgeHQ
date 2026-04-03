# FORGEHQ Comprehensive Test Plan

**Document version:** 1.0 (2026-04-03) — QA protocol foundation  
**Generated from:** `SYSTEM.md` version 1.2 (2026-04-03)  
**Repo maturity:** contract/bootstrap repo with a Phase 1 scaffold, not a live shaping service

---

## 1. Testing Philosophy and Guiding Principles

forgeHQ currently implements governance contracts, documentation assembly infrastructure, typed schema stubs, and a no-op but valid pipeline scaffold. It does **not** currently implement a frontend, API, persistence layer, live shaping workers, or cross-service runtime behavior. This plan is therefore spec-first and maturity-bounded: it validates the current `SYSTEM.md` truth without fabricating unsupported later-tier coverage.

### 1.1 Guiding Principles

| Principle | Local interpretation for forgeHQ |
| --- | --- |
| Fail-closed | Invalid stage order, missing predecessor artifacts, documentation drift, and missing QA tooling must fail explicitly |
| Spec-first | Coverage is derived from `SYSTEM.md`, `doc/system/`, and current repo contracts, not assumed future runtime behavior |
| Honest applicability | Tiers without a real repo surface are marked `not applicable yet` with a concrete rationale |
| Non-authoritative posture | Tests must preserve the repo boundary that forgeHQ proposes candidates but does not become the upstream authority |
| Lightweight by design | Current tests favor contract, script, and pipeline validation over fictional UI or service flows |

### 1.2 Current Testing Mode

- Default testing mode is **Mode A (Monorepo / local-only)**.
- Mode A is sufficient for current forgeHQ because the repo has no live external runtime dependencies yet.
- Mode B is deferred until forgeHQ grows real API, persistence, or multi-service flows.

## 2. Tier Overview and Planned Counts

| Tier | Name | Applicability | Current planned coverage |
| --- | --- | --- | --- |
| T0 | Infrastructure Pre-Flight | Applicable now | 5 mandatory pre-flight checks plus runner discovery |
| T1 | Unit and Contract Tests | Applicable now | Current contract, worker, pipeline, and QA-foundation pytest suites |
| T2 | Component Tests | Not applicable yet | No browser, desktop, or operator UI exists in this repo |
| T3 | API Contract Tests | Not applicable yet | No HTTP or RPC routes exist in this repo |
| T4 | Integration Tests | Not applicable yet | No multi-module live runtime exists yet |
| T5 | E2E User Journeys | Not applicable yet | No end-user runtime flow exists yet |
| T6 | Performance and Load | Limited applicability now | Informational command-budget checks for docs/test tooling only |
| T7 | Platform and Packaging | Not applicable yet | No packaged runtime, service image, or release artifact exists yet |
| T8 | Accessibility | Not applicable yet | No UI exists to audit for keyboard or screen-reader behavior |

## 3. Detailed Tier Mapping by Current Repo Surface

Every currently documented repo surface from `SYSTEM.md` is mapped below to at least one applicable tier or an explicit defer-until-later rationale.

| Surface | Current truth | Tier mapping |
| --- | --- | --- |
| `docs/architecture/forgehq-system-role.md` | Defines repo authority boundary | T1 contract verification; smoke-adjacent via repo test suite |
| `docs/contracts/reviewability-contract.md` | Defines reviewability rules and lifecycle boundaries | T1 contract verification |
| `app/domain/artifacts/enums.py` | Artifact families and reviewability backbone | T1 via governance enum tests; smoke suite |
| `app/domain/pipeline/enums.py` | Stage order and owner registry | T1 via governance and progression tests; smoke suite |
| `app/domain/reviewability/enums.py` | Language posture and lifecycle separation | T1 via governance tests |
| `app/domain/workers/enums.py` | Worker ownership and emission boundaries | T1 via worker boundary tests |
| `app/schemas/` | Typed placeholder artifacts and `ShapingRun` model | T1 via schema contract tests |
| `app/orchestration/stage_router.py` | Fail-closed stage progression and artifact prerequisites | T1 via progression and rejection tests; smoke suite |
| `app/orchestration/forgehq_orchestrator.py` | No-op placeholder artifact emission in valid order | T1 via progression tests; smoke suite |
| `CLAUDE.md` | Repo-local coding and testing instructions | T1 documentation-surface verification |
| `docs/forge_hq_architecture_spec.md` | Current architecture truth and boundary map | T1 documentation-surface verification |
| `docs/forge_hq_extended_roadmap.md` | Phase status and future slice intent | T1 documentation-surface verification |
| `doc/system/_index.md` and numbered part files | Canonical modular system source | T0 build and parity checks; T1 documentation protocol tests; smoke suite |
| `SYSTEM.md` | Generated root system reference | T0 parity check through build; T1 documentation protocol tests; smoke suite |
| `scripts/context-bundle.sh` | Selective context loader | T0 `--list` and `--dry-run`; T1 documentation protocol tests; smoke suite |
| `docs/reference/bds/` | Imported company-core doctrine references | T1 documentation protocol tests; scope reference only |
| `FORGEHQ_COMPREHENSIVE_TEST_PLAN.md` | Canonical QA plan for current maturity | T1 QA-foundation contract test |
| `docs/qa/FORGEHQ_MODE_A_T0_CHECKLIST.md` | Human-readable T0 checklist | T1 QA-foundation contract test |
| `docs/qa/FORGEHQ_QA_FINDINGS_LOG_TEMPLATE.md` | BugCheck-style findings capture template | T1 QA-foundation contract test |
| `docs/qa/FORGEHQ_QA_RUN_REPORT_TEMPLATE.md` | Run-report template for tier execution | T1 QA-foundation contract test |
| `docs/qa/FORGEHQ_TIER_APPLICABILITY_MATRIX.md` | Explicit applicability rules for T0-T8 | T1 QA-foundation contract test |
| `scripts/qa-mode-a-preflight.sh` | Executable Mode A T0 pre-flight | T0 operational check surface; T1 checklist exposure test |
| `scripts/qa-regression-smoke.sh` | Lightweight regression smoke suite | T1 script exposure test; manual/CI smoke command surface |
| `tests/contract/` | Contract and documentation tests | T1 direct |
| `tests/pipeline/` | Stage-order and reviewability gate tests | T1 direct; smoke suite |
| `tests/workers/` | Worker emission boundary tests | T1 direct |
| Browser UI | Not implemented | T2 and T8 not applicable until UI exists |
| Desktop UI | Not implemented | T2 and T8 not applicable until UI exists |
| Operator dashboard | Not implemented in this repo | T2 and T8 not applicable until downstream review UI exists |
| HTTP routes | Not implemented | T3 not applicable until API exists |
| Request schemas and auth middleware | Not implemented | T3 not applicable until API exists |
| SQL migrations and ORM models | Not implemented | T0 database checks and T3/T4 database-backed flows deferred until persistence exists |
| Artifact registry tables and lineage tables | Not implemented | T0 DB checks and T4/T5 flows deferred until persistence exists |
| ForgeEval / ForgeMath / DataForge / ForgeCommand integrations | Declared boundaries only | T4/T5 deferred until adapters and live flows exist |

## 4. Detailed Checks per Tier

### 4.1 T0 — Infrastructure Pre-Flight

Mode A T0 is mandatory for the current repo. The applicable checks are:

| Check | Command | Expected result |
| --- | --- | --- |
| Documentation build succeeds | `bash doc/system/BUILD.sh` | exits `0` and reports `SYSTEM.md assembled` |
| Context bundle listing succeeds | `bash scripts/context-bundle.sh --list` | exits `0` and prints available sections and presets |
| Context bundle dry run succeeds | `bash scripts/context-bundle.sh --dry-run --preset core --with-roadmap` | exits `0` and prints assembled section list |
| Pytest runner exists | `scripts/qa-mode-a-preflight.sh` auto-detects repo `.venv`, `../DataForge/.venv`, or `python3 -m pytest` | runner path or command is resolved without ambiguity |
| Repo test suite passes | detected pytest runner against repo tests | exits `0`; no unresolved S0/S1 regression |

### 4.2 T1 — Unit and Contract Tests

Current applicable T1 suites:

| Test file | Primary assertion target |
| --- | --- |
| `tests/contract/test_governance_enums.py` | artifact families, stage order, language posture, lifecycle-state separation |
| `tests/workers/test_worker_emission_boundaries.py` | worker-stage ownership and emission boundaries |
| `tests/contract/test_artifact_schemas.py` | non-authoritative schema defaults and shaping-run posture |
| `tests/pipeline/test_stage_progression.py` | valid end-to-end no-op stage progression and skip rejection |
| `tests/pipeline/test_design_required_before_generation.py` | design-before-generation gate |
| `tests/pipeline/test_reviewability_requires_challenge_and_verification.py` | packaging block without falsification or verification |
| `tests/contract/test_documentation_protocol.py` | `SYSTEM.md` build parity, context-bundle behavior, required docs |
| `tests/contract/test_qa_protocol_foundation.py` | QA plan, templates, checklist, and smoke-suite definitions |

### 4.3 T2 — Component Tests

Not applicable yet. `SYSTEM.md` explicitly documents that forgeHQ has no browser UI, desktop UI, or operator dashboard in this repo.

### 4.4 T3 — API Contract Tests

Not applicable yet. `SYSTEM.md` explicitly documents that forgeHQ exposes no HTTP or RPC API.

### 4.5 T4 — Integration Tests

Not applicable yet. There is no live multi-module runtime, no persistence layer, and no active adapters to upstream or downstream systems.

### 4.6 T5 — E2E User Journeys

Not applicable yet for execution. The future journey inventory derived from current architecture intent is:

1. admitted signal intake to target ranking to context bundle assembly
2. context bundle to candidate design to candidate patch generation
3. candidate patch to falsification to verification to proposal packaging
4. packaged proposal to DataForge persistence with lineage retention
5. packaged proposal to ForgeCommand review queue with operator-state linkage

These are recorded to keep future QA planning spec-first, but none are executable in the current repo.

### 4.7 T6 — Performance and Load

Limited applicability now. No render, API, database, concurrency, or load benchmarks are legitimate yet. The only current T6 coverage is lightweight tooling responsiveness recorded for trend monitoring, not release marketing:

| Check | Status | Measurement posture |
| --- | --- | --- |
| `bash doc/system/BUILD.sh` | Applicable now | soft target: completes in under 5 seconds on a local dev machine |
| `bash scripts/context-bundle.sh --dry-run --preset core --with-roadmap` | Applicable now | soft target: completes in under 3 seconds on a local dev machine |
| `bash scripts/qa-regression-smoke.sh` | Applicable now | soft target: completes in under 15 seconds on a local dev machine |
| UI render budgets | Deferred | no UI exists |
| API latency budgets | Deferred | no API exists |
| database query/load tests | Deferred | no persistence layer exists |

These thresholds are informational and drift-detection only until a stable CI baseline exists.

### 4.8 T7 — Platform and Packaging

Not applicable yet. The repo currently ships no desktop package, server image, wheel, container, or release bundle.

### 4.9 T8 — Accessibility

Not applicable yet. Accessibility testing begins when forgeHQ owns an actual UI surface.

## 5. E2E Journey Scenarios

The protocol requires journey scenarios even when execution is deferred. forgeHQ records the following future journeys as placeholders tied to current architecture intent:

| Journey | Planned future scope | Current status |
| --- | --- | --- |
| Journey 1 | signal intake to ranked target selection | Deferred until Phase 2 runtime exists |
| Journey 2 | context curation to candidate design | Deferred until Phase 2/3 runtime exists |
| Journey 3 | design to patch generation to falsification | Deferred until Phase 3/4 runtime exists |
| Journey 4 | verification to proposal packaging to persistence | Deferred until persistence exists |
| Journey 5 | proposal rendering and operator review flow | Deferred until ForgeCommand-facing UI exists |

## 6. Test Data Strategy

- Current tests use only tracked repository files and in-memory dataclass artifacts.
- No database seed script exists because no database exists in the current repo.
- No network fixtures exist because the repo has no live API or adapter calls yet.
- Artifact lineage in tests is represented through deterministic placeholder `artifact_id` relationships and explicit parent references.
- Documentation tests use the tracked `doc/system/` source tree as canonical input and treat generated `SYSTEM.md` parity as the invariant.
- When persistence appears later, this plan must grow a real seed, cleanup, and fixture strategy before claiming T3-T5 completeness.

## 7. Tooling Setup Checklist

- Bash available locally
- `doc/system/BUILD.sh` available
- `scripts/context-bundle.sh` available
- `scripts/qa-mode-a-preflight.sh` available
- `scripts/qa-regression-smoke.sh` available
- `pytest` available through one of:
  - `PYTEST_RUNNER=/absolute/path/to/pytest`
  - `./.venv/bin/pytest`
  - `../DataForge/.venv/bin/pytest`
  - `python3 -m pytest`
- `SYSTEM.md` current before executing or updating this plan
- Mode declaration recorded in the run report before test execution

## 8. Definition of Done for Current Repo Maturity

The QA gate for the current maturity level is met only when:

1. `SYSTEM.md` and `doc/system/` are in parity.
2. The comprehensive test plan and QA templates are current with repo truth.
3. Mode A T0 pre-flight passes.
4. The regression smoke suite passes.
5. The full pytest suite passes.
6. Tier applicability remains explicitly classified for T0 through T8.
7. No unresolved S0 or S1 findings remain in the findings log.
8. No documentation or test claim implies that forgeHQ is already a live shaping service.

## 9. BugCheck Run Report Template

The canonical run-report template lives in `docs/qa/FORGEHQ_QA_RUN_REPORT_TEMPLATE.md`. Minimum required fields are:

- run metadata: date, operator, branch, commit, mode
- repo maturity declaration
- tier applicability summary
- commands executed
- pass/fail outcome per tier
- durations for applicable T0/T6 command checks
- findings summary with severity counts
- release/gate decision

## 10. Regression Smoke Suite Specification

The lightweight smoke suite for the current repo is intentionally narrow:

| Step | Command | Purpose |
| --- | --- | --- |
| 1 | `bash doc/system/BUILD.sh` | verify documentation build parity |
| 2 | `bash scripts/context-bundle.sh --dry-run --preset core --with-roadmap` | verify selective context assembly inputs |
| 3 | `pytest tests/contract/test_governance_enums.py` | lock core governance vocabulary |
| 4 | `pytest tests/pipeline/test_stage_progression.py` | verify valid ordered progression and skip rejection |
| 5 | `pytest tests/pipeline/test_design_required_before_generation.py` | keep generation blocked before design |
| 6 | `pytest tests/pipeline/test_reviewability_requires_challenge_and_verification.py` | keep packaging blocked before falsification and verification |

The executable wrapper for this suite is `scripts/qa-regression-smoke.sh`.
