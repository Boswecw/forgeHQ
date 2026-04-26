# ForgeHQ Architecture Specification

Date/Time: 2026-04-26T00:00:00-04:00  
Status: Active documentation protocol surface  
System: ForgeHQ  
Scope: Internal BDS Forge ecosystem shaping and proposal bridge system

## 1. System Role

ForgeHQ is the governed shaping and proposal layer for Charlie's internal Forge ecosystem. It receives bounded upstream evidence, normalizes proposal context, and prepares operator-reviewable proposal artifacts. ForgeHQ does not replace deterministic authority systems and does not act as an unbounded autonomous implementation agent.

## 2. Boundary Position

ForgeHQ sits downstream of evidence-producing systems and upstream of operator approval surfaces.

Current evaluation-spine boundary:

1. Forge Eval produces governed evaluation evidence bundles.
2. Eval Cal Node produces calibration reports from evaluation evidence.
3. ForgeMath produces lane-level authority references from calibration reports.
4. ForgeHQ consumes approved upstream references and prepares proposal-bridge payloads.
5. ForgeCommand remains the operator-facing control and approval surface.

## 3. Authority Rules

ForgeHQ may:

- assemble proposal context,
- preserve upstream evidence references,
- compute deterministic proposal payload hashes,
- prepare reviewable proposal metadata,
- fail closed when required upstream evidence is missing.

ForgeHQ may not:

- mutate upstream evidence,
- bypass ForgeMath authority references,
- self-approve implementation,
- silently degrade missing evidence,
- replace ForgeCommand operator approval.

## 4. Documentation Protocol Role

This file is a required documentation protocol surface. It exists so repository-level tests can prove that ForgeHQ has a stable architecture-spec anchor before proposal bridge behavior is accepted as governed.

## 5. Phase 06 Addition

Phase 06 adds the evaluation spine proposal bridge. The bridge accepts:

- Forge Eval evidence bundle references,
- Eval Cal Node calibration report payloads,
- ForgeMath lane evaluation references,

and emits ForgeHQ upstream evidence references suitable for later proposal shaping and operator review.

## 6. Current Acceptance Boundary

A valid Phase 06 proof requires:

- import boundary success,
- targeted evaluation spine proposal bridge tests passing,
- full repository test sweep passing,
- documentation protocol surfaces present,
- context bundle dry-run roadmap flag support intact,
- clean git status after commit and tag.
