# forgeHQ — Claude Instructions

## Module Map

| Module | Surface | Primary Files | Current Authority |
|--------|---------|---------------|-------------------|
| System Role Docs | Repo governance boundary | `docs/architecture/forgehq-system-role.md` | Defines what forgeHQ may and may not do |
| Artifact Contracts | Artifact vocabulary and reviewability backbone | `app/domain/artifacts/enums.py` | Defines non-authoritative artifact families and lineage layers |
| Pipeline Contracts | Stage order and stage-to-worker ownership | `app/domain/pipeline/enums.py` | Defines the no-skip pipeline order |
| Reviewability Contracts | Reviewability, lifecycle, and language posture | `app/domain/reviewability/enums.py` | Keeps proposal lifecycle separate from operator decision state |
| Worker Contracts | Worker identities and emission boundaries | `app/domain/workers/enums.py` | Keeps generator and critic lanes structurally independent |
| Schema Stubs | Phase 1 artifact and run scaffolding | `app/schemas/` | Defines typed non-authoritative artifact placeholders and shaping runs |
| Orchestration Skeleton | Stage validation and no-op progression | `app/orchestration/` | Enforces ordered stage progression without adding live runtime semantics |
| Documentation Assembly | Canonical repo context | `doc/system/`, `SYSTEM.md`, `scripts/context-bundle.sh` | Provides the build surface for repo truth |
| QA Foundation | QA planning, templates, and executable checks | `FORGEHQ_COMPREHENSIVE_TEST_PLAN.md`, `docs/qa/`, `scripts/qa-*.sh` | Keeps QA claims aligned with actual repo maturity |
| Imported BDS Protocols | Cross-ecosystem doctrine reference | `docs/reference/bds/` | Reference-only company-core protocols that inform repo standards |
| Contract Tests | Governance, documentation, and pipeline verification | `tests/contract/`, `tests/pipeline/`, `tests/workers/` | Guards bounded repo behavior |

## Coding Standards

- Use Python 3.12+ and standard-library-first contracts unless a new phase explicitly requires more.
- Keep forgeHQ non-authoritative. This repo proposes and evaluates candidates; it does not mint canonical upstream truth.
- Fail closed on ambiguity, missing artifacts, invalid stage transitions, and scope escape.
- Keep proposal lifecycle state separate from operator decision state at both code and documentation levels.
- Preserve structural independence between generator and critic/falsifier lanes.
- Treat Phase 1 orchestration as a placeholder pipeline scaffold, not as a live shaping runtime.
- Do not add API, persistence, or orchestration logic unless the current phase explicitly calls for it.

## File Conventions

- Runtime/domain code lives under `app/`.
- Contract and system docs live under `docs/` and `doc/system/`.
- Phase 1 schema stubs live under `app/schemas/`.
- Phase 1 stage-routing logic lives under `app/orchestration/`.
- Imported ecosystem doctrine references live under `docs/reference/bds/`.
- QA support docs live under `docs/qa/`.
- Root `SYSTEM.md` is a build artifact assembled from `doc/system/` parts.
- Root `FORGEHQ_COMPREHENSIVE_TEST_PLAN.md` is the current QA plan for repo maturity.
- New tests live under `tests/`.
- Repo automation scripts live under `scripts/`.

## Context Loading

```bash
# Core repo posture
./scripts/context-bundle.sh --preset core

# Governance and reviewability work
./scripts/context-bundle.sh --preset governance --with-roadmap

# Documentation-stack maintenance
./scripts/context-bundle.sh --preset docs
```

## Ecosystem Rules

- ForgeEval and ForgeMath remain upstream authorities where adopted; forgeHQ consumes their outputs but does not overwrite them.
- DataForge is the downstream persistence boundary; do not make forgeHQ the canonical persistence authority.
- ForgeCommand is the downstream operator surface; do not collapse operator action state into forgeHQ workflow state.
- No direct merge authority, approval authority, or hidden autonomous action belongs in this repo.

## Testing Expectations

- Run `python3 -m pytest` when local `pytest` is installed, or use an existing repo virtualenv.
- Run `scripts/qa-mode-a-preflight.sh` before claiming QA readiness for the current repo maturity.
- Run `scripts/qa-regression-smoke.sh` for the lightweight regression gate.
- Keep contract tests for artifact families, worker boundaries, stage routing, and documentation build surfaces green.
- Keep the QA plan and applicability matrix honest; do not invent T2-T8 coverage before those surfaces exist.
- Update `doc/system/` and rebuild `SYSTEM.md` whenever repo truth changes.

## Change Protocol

- Edit `doc/system/` parts, never root `SYSTEM.md`, then run `doc/system/BUILD.sh`.
- Keep changes bounded to the current implementation phase.
- Prefer patches over broad rewrites.
- If architectural truth changes, update code contracts, `docs/`, and `doc/system/` in the same turn.
