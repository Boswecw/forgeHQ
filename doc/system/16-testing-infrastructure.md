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
