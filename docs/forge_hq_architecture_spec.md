# forgeHQ Architecture Spec

**Document version:** 1.2 (2026-04-03) — Phase 1 stage scaffold plus QA foundation

## 1. Purpose

forgeHQ is the bounded proposal-generation and confidence-shaping subsystem for the BDS ecosystem.
Its job is to transform admitted evidence and weak-confidence signals into reviewable candidate improvements without claiming canonical upstream truth or human decision authority.

## 2. Current implementation state

The current repository state implements:

- phase-0 governance contracts
- phase-1 shaping run scaffold
- artifact family vocabulary
- pipeline stage vocabulary
- worker emission boundaries
- reviewability and language posture enums
- typed schema stubs for required core artifacts
- strict stage router with fail-closed transition enforcement
- no-op orchestrator that emits placeholder artifacts in stage order
- repo-level documentation assembly compliant with the documentation protocol
- repo-level QA protocol foundation aligned to current maturity

The current repository state does not implement:

- HTTP endpoints
- live ranking, curation, generation, falsification, or verification services
- persistence models or migrations
- DataForge adapters
- ForgeCommand read models

## 3. Module map

| Area | Current files | Responsibility |
| --- | --- | --- |
| Artifact domain | `app/domain/artifacts/enums.py` | Artifact families, lineage layers, reviewability backbone |
| Pipeline domain | `app/domain/pipeline/enums.py` | Stage ordering and stage ownership |
| Reviewability domain | `app/domain/reviewability/enums.py` | Reviewability requirements, downgrade reasons, language posture |
| Worker domain | `app/domain/workers/enums.py` | Worker names and allowed emissions |
| Schema stubs | `app/schemas/` | Typed placeholders for shaping runs and required artifact families |
| Orchestration skeleton | `app/orchestration/` | Stage router and no-op ordered progression |
| Governance docs | `docs/architecture/`, `docs/contracts/` | Repo truth boundaries and doctrine |
| QA protocol foundation | `FORGEHQ_COMPREHENSIVE_TEST_PLAN.md`, `docs/qa/`, `scripts/qa-*.sh` | Mode A pre-flight, smoke suite, templates, and applicability rules |
| Imported BDS protocols | `docs/reference/bds/` | Cross-ecosystem reference doctrine, not repo-local truth |
| System reference | `doc/system/`, `SYSTEM.md` | Canonical assembled repo reference |
| Contract tests | `tests/contract/`, `tests/pipeline/`, `tests/workers/` | Verification of bounded repo posture |

## 4. Target internal architecture

The intended repo shape remains:

```text
forgeHQ/
  app/
    domain/
      artifacts/
      pipeline/
      reviewability/
      workers/
    schemas/
    orchestration/
    api/
    services/
    persistence/
    read_models/
    domain/adapters/
  tests/
  docs/
  doc/system/
  scripts/
```

The current repo now has the domain-contract slice, typed schema stubs, and a no-op stage-orchestration skeleton.

## 5. Architectural laws

- forgeHQ may consume ForgeEval evidence and ForgeMath outputs but may not overwrite them as canonical truth
- proposal lifecycle state must remain separate from operator decision state
- no proposal is reviewable without challenge and verification
- all forgeHQ artifacts carry explicit non-authoritative posture
- ambiguity, missing artifacts, and scope escape fail closed

## 6. External boundaries

| System | Boundary posture | Current integration status |
| --- | --- | --- |
| ForgeEval | Upstream deterministic evidence | Declared boundary only |
| ForgeMath | Upstream math/rule authority where adopted | Declared boundary only |
| DataForge | Downstream persistence and lineage | Declared boundary only |
| ForgeCommand | Downstream review surface and operator action state | Declared boundary only |

## 7. Documentation stack

This repo now follows the documentation protocol with:

- root `CLAUDE.md`
- modular `doc/system/` source files
- `doc/system/BUILD.sh`
- generated root `SYSTEM.md`
- `scripts/context-bundle.sh`
- architecture and roadmap documents in `docs/`
- imported company-core doctrine references in `docs/reference/bds/`
- Phase 1 pipeline tests and schema contract tests
- QA plan, templates, and executable smoke/pre-flight scripts for current maturity

## 8. Immediate next architectural step

The next implementation slice is Phase 2: add admitted signal intake, target ranking, and bounded context curation on top of the Phase 1 scaffold.
