# forgeHQ — Codex Agent Guidance

This file is the standing operating doctrine for Codex (and any AI agent) working
inside this repository. Read it before every implementation turn.

---

## System Role

forgeHQ is the bounded proposal-generation and confidence-shaping subsystem for
the BDS ecosystem.

**What it is:**
- consumes upstream evidence and weak-confidence signals
- ranks candidate improvement targets
- builds bounded context packs
- designs candidate changes before generation
- generates bounded candidate artifacts
- challenges those candidates through falsification
- verifies candidate outcome
- assembles non-authoritative proposal packages for human review

**What it is NOT:**
- not deterministic truth
- not approval authority
- not merge authority
- not canonical persistence authority

---

## Hard Non-Goals

Never implement these inside forgeHQ:

1. Claiming deterministic repo truth
2. Overwriting ForgeEval truth
3. Overwriting ForgeMath truth
4. Making approval decisions
5. Executing autonomous merges
6. Collapsing proposal lifecycle state into human decision state

---

## Upstream / Downstream Boundaries

| Direction | System | Relationship |
|-----------|--------|--------------|
| Upstream | ForgeEval | Deterministic evidence substrate — consume only, never overwrite |
| Upstream | ForgeMath | Governed math authority — consume only, never overwrite |
| Downstream | DataForge | Persistence of lineage, artifacts, proposals, review linkage |
| Downstream | ForgeCommand | Human review surface and operator action state |

---

## Artifact Families

All artifact families are defined in `app/domain/artifacts/enums.py`.

| Family | Stage | Required for backbone? |
|--------|-------|------------------------|
| `signal_snapshot` | SIGNAL_INTAKE | Yes |
| `intake_diagnostics` | SIGNAL_INTAKE | No |
| `target_ranking` | TARGET_RANKING | Yes |
| `ranking_factor_trace` | TARGET_RANKING | No |
| `context_bundle` | CONTEXT_CURATION | Yes |
| `candidate_design` | CANDIDATE_DESIGN | Yes |
| `candidate_patch` | CANDIDATE_GENERATION | Yes |
| `falsification_report` | FALSIFICATION | Yes |
| `candidate_verification` | VERIFICATION | Yes |
| `confidence_shaping_summary` | PROPOSAL_PACKAGING | Yes |
| `forgehq_proposal` | PROPOSAL_PACKAGING | Yes |
| `forgehq_evidence_bundle` | PROPOSAL_PACKAGING | No |

Every artifact must carry `authority_posture = NON_AUTHORITATIVE`.

---

## Stage Sequencing Rules

Stages are defined in `app/domain/pipeline/enums.py`. They are strictly ordered
and may not be skipped.

```
SIGNAL_INTAKE
  → TARGET_RANKING
  → CONTEXT_CURATION
  → CANDIDATE_DESIGN
  → CANDIDATE_GENERATION
  → FALSIFICATION
  → VERIFICATION
  → PROPOSAL_PACKAGING
```

**Hard gates enforced by the stage router:**
- `CANDIDATE_GENERATION` requires `CANDIDATE_DESIGN` artifact present
- `PROPOSAL_PACKAGING` requires `FALSIFICATION_REPORT` and `CANDIDATE_VERIFICATION` present

---

## Reviewability Rules

A proposal may only be `reviewable` when ALL of the following are true:
- design present
- candidate present
- challenge (falsification) present
- verification present
- non-authoritative notice present
- explicit scope boundary statement present
- parent refs valid
- no unresolved scope escape
- no broken lineage condition

**Automatic `not_reviewable` conditions:**
- missing challenge artifact
- missing verification artifact
- missing source refs
- scope escape detected
- invalid parent evidence refs
- confidence summary missing downgrade factors
- rollback class required but absent

---

## Fail-Closed Requirements

Fail closed means: raise an explicit error, do not silently degrade.

- Unknown signal source ref schemes → `NoAdmittedSourcesError`
- Placeholder artifact in service boundary → `RankingError` / `ScopeEscapeError`
- Scope exceeds policy → `ScopeEscapeError`
- Invalid stage transition → `InvalidStageTransitionError`
- Missing required predecessor artifact → `MissingRequiredArtifactError`
- Missing backbone artifact at packaging → `not_reviewable` state

Never return a degraded result silently. Always surface the failure explicitly.

---

## Non-Authoritative Language Posture

### Allowed language in all artifacts and summaries
- propose, hypothesize, suggest, indicate, candidate, challenge
- "observed candidate gain", "reviewability state", "residual concern"

### Prohibited language — never use in any forgeHQ artifact
- approved, confirmed fix, proven truth, authoritative state, must apply, merge now

Language validators are in `app/domain/reviewability/enums.py`.

---

## Worker Ownership

Workers are defined in `app/domain/workers/enums.py`.

| Worker | Owns |
|--------|------|
| Signal Analyst | signal_snapshot, intake_diagnostics, target_ranking, ranking_factor_trace |
| Context Curator | context_bundle |
| Designer | candidate_design |
| Generator | candidate_patch |
| Critic / Falsifier | falsification_report |
| Verifier | candidate_verification |
| Proposal Assembler | confidence_shaping_summary, forgehq_proposal, forgehq_evidence_bundle |
| Orchestrator | no artifact ownership |

**The critic lane must remain structurally independent from the generator lane.**
A worker must never emit artifacts from another worker's family.

---

## Source Ref URI Schemes

Signal source refs are classified by URI scheme prefix:

| Scheme | Authority Class | Admitted? |
|--------|----------------|-----------|
| `forgeeval://` | `deterministic_evidence` | Yes |
| `forgemath://` | `governed_math` | Yes |
| `signal://` | `weak_signal` | Yes |
| anything else | `unknown` | **No — rejected at intake** |

Deterministic factors (`is_deterministic=True`) receive 2× weight in composite
ranking scoring to structurally privilege ForgeEval/ForgeMath evidence.

---

## Coding Standards

- Python 3.12+, standard-library-first unless a phase explicitly requires more
- `StrEnum` for all domain enumerations
- Frozen dataclasses with `slots=True` for all artifact schemas
- No external I/O, no persistence, no network calls in service logic
- Type hints on every function signature
- Bounded changes per phase — do not add Phase N+1 logic in Phase N

---

## Testing Expectations

- `python3 -m pytest tests/ -q` must pass before claiming a slice complete
- Each service must have tests covering: fail-closed behavior, valid output shape,
  non-authoritative posture, and artifact family correctness
- Do not add T2-T8 coverage claims before those surfaces exist

---

## Change Protocol

1. Edit `doc/system/` part files, not root `SYSTEM.md`
2. Run `bash doc/system/BUILD.sh` after doc changes
3. Keep changes bounded to the current implementation phase
4. Verify `python3 -m pytest tests/ -q` is green before finishing

---

## Current Implementation Status

| Phase | Status |
|-------|--------|
| Phase 0 — Boundary Freeze | Complete |
| Phase 1 — Core Artifact and Orchestrator Skeleton | Complete |
| Phase 2 — Ranking and Context Slice | Complete |
| Phase 3 — Design and Generation Slice | Complete |
| Phase 4 — Critic and Verification Slice | Complete |
| Phase 5 — Proposal Packaging and Persistence | Complete |
| Phase 6 — ForgeCommand Integration | Complete |
| Phase 7 — Hardening and Scale-Out | Not started |
