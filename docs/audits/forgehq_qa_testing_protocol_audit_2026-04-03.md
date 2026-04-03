# forgeHQ QA Testing Protocol Audit

**Audit date:** 2026-04-03  
**Protocol basis:** `BDS_QA_TESTING_PROTOCOL.md`  
**Repo state audited:** Phase 1 baseline with 23 passing pytest tests

## Scope

This audit compares the current `forgeHQ` repository against the required five-phase QA lifecycle and eight-tier testing model defined in `BDS_QA_TESTING_PROTOCOL.md`.

## Observed baseline

- `SYSTEM.md` exists and is current enough to describe the Phase 1 scaffold.
- The repo has a small passing pytest suite covering governance, documentation, and pipeline scaffolding.
- The repo remains a contract/bootstrap repository with no API, UI, persistence layer, or live runtime services.

## Findings

### 1. S1 — No spec-first comprehensive test plan artifact exists

**Affected phase/tier:** Phase 1 PLAN, Phase 2 AUDIT, all downstream tiers

**What is missing or wrong**

The protocol requires a spec-first Markdown test plan named `{APP}_COMPREHENSIVE_TEST_PLAN.md` with tier mapping, test counts, E2E journeys, performance targets, test data strategy, tooling checklist, Definition of Done, BugCheck run-report template, and regression-smoke specification. No such artifact exists in the repository.

**Why it matters**

Without the plan, current tests cannot be traced back to `SYSTEM.md` coverage. The repo therefore cannot honestly claim Phase 1 PLAN or Phase 2 AUDIT completion under the protocol.

**Specific fix**

Create `FORGEHQ_COMPREHENSIVE_TEST_PLAN.md` at the repo root or under a clearly referenced QA docs surface. Generate it from `SYSTEM.md`, include all ten required sections, and map every documented repo surface to at least one tier or an explicit `not-applicable-yet` rationale.

### 2. S1 — No Phase 2 audit artifact exists for spec-vs-plan comparison

**Affected phase/tier:** Phase 2 AUDIT

**What is missing or wrong**

The protocol requires a numbered audit findings document comparing `SYSTEM.md` line-by-line against the test plan, with fixes applied back to the plan and the net test-count change documented. The repo currently has no audited test plan because the prerequisite plan does not exist.

**Why it matters**

This prevents the repo from proving that the documented Phase 1 scaffold is fully represented in QA coverage, especially for newer surfaces such as `app/schemas/` and `app/orchestration/`.

**Specific fix**

After creating the comprehensive plan, add a dedicated QA audit document that enumerates missing coverage, wrong names, missing failure modes, and tier gaps, then version the plan after applying those findings.

### 3. S1 — T0 pre-flight has not been formalized, logged, or gated

**Affected phase/tier:** Phase 3 INFRA / T0

**What is missing or wrong**

The protocol requires a T0 pre-flight with executed checks, a findings log, zero unresolved S0/S1 issues, and a declared testing mode before any T1 work proceeds. The repo has only `scripts/context-bundle.sh`; there is no QA pre-flight script, no T0 checklist artifact, no findings table, and no testing-mode declaration.

**Why it matters**

Even for a contract-only repo, there are meaningful T0 checks: Python/test environment availability, `SYSTEM.md` build integrity, context-bundle integrity, and the current pytest baseline. Those checks are currently implicit and not archived.

**Specific fix**

Create a small `Mode A` T0 pre-flight for this repo, likely shell-based, that verifies:

- `doc/system/BUILD.sh` succeeds
- `scripts/context-bundle.sh --list` and `--dry-run` succeed
- the selected pytest runner exists
- the repo test suite passes

Record findings in the test plan and explicitly declare that only `Mode A` is applicable until live services exist.

### 4. S2 — BugCheck compliance artifacts are absent

**Affected phase/tier:** All phases

**What is missing or wrong**

The protocol requires BugCheck schema availability plus structured findings and run-report usage. The repository does not currently contain `finding.schema.json`, `enrichment.schema.json`, lifecycle-event schemas, or any BugCheck run report artifact.

**Why it matters**

The current test suite passes, but QA findings cannot be logged in the required format, and no release/audit report can be produced in a protocol-compliant way.

**Specific fix**

Import or vendor the required BugCheck schemas into a stable repo location and add a QA findings log plus run-report template linked from the comprehensive plan.

### 5. S2 — Tier applicability is undocumented beyond the current pytest suite

**Affected phase/tier:** Phase 4 BUILD, Phase 5 GATE

**What is missing or wrong**

The repo has real T1-style tests, but there is no documented applicability matrix for T2–T8. Because `forgeHQ` currently has no frontend, no API routes, no persistence, and no packaging surface, many later tiers are not yet applicable. The protocol still requires those tiers to be planned and explicitly classified rather than silently omitted.

**Why it matters**

As written, the repo appears to have stopped after ad hoc T1-style implementation. That is acceptable for current maturity only if the non-applicable tiers are explicitly documented and revisited when new surfaces arrive.

**Specific fix**

In the comprehensive plan, add a tier applicability matrix such as:

- `T0`: applicable now
- `T1`: applicable now
- `T2`: not applicable until UI exists
- `T3`: not applicable until API exists
- `T4/T5`: not applicable until live runtime and multi-module flows exist
- `T6`: limited applicability now for command/runtime budgets; full applicability later
- `T7`: not applicable until packaging targets exist
- `T8`: not applicable until UI exists

### 6. S3 — No regression smoke suite or release gate artifact exists

**Affected phase/tier:** Phase 5 GATE

**What is missing or wrong**

The protocol expects a regression smoke suite specification and a release-readiness gate/report. The repo currently has neither.

**Why it matters**

This does not block the current Phase 1 contract work, but it means the repo cannot claim protocol-compliant release readiness even for a future internal beta without more QA infrastructure.

**Specific fix**

Define a lightweight smoke suite around:

- documentation build parity
- context-bundle dry run
- governance enum tests
- pipeline progression tests

Then add a simple release-gate checklist and run-report template to the QA plan.

## Non-findings

- The existing pytest baseline is stable: 23 tests passed during this audit.
- The repo’s current lack of frontend, API, persistence, and packaging surfaces is documented in `SYSTEM.md`; those missing product surfaces are not themselves QA defects.

## Recommended next step

1. Create `FORGEHQ_COMPREHENSIVE_TEST_PLAN.md`.
2. Declare `Mode A` T0 for the current contract-only repo.
3. Import BugCheck schemas and start a findings log.
4. Re-audit the plan against `SYSTEM.md`.
