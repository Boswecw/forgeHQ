# forgeHQ — Compiled System Reference

**Designation:** FRG
**Document role:** Canonical compiled technical reference for the forgeHQ proposal-shaping service
**Source:** `doc/system/`
**Build command:** `bash doc/system/BUILD.sh`
**Document version:** 2.0 (2026-06-19) — BDS canonical-compliance migration (7-group class-aware structure, truth classes, designation-bound fail-closed assembly, authored governance trio)
**Protocol:** BDS Documentation Protocol v2.0; BDS Repo Documentation System Canonical Compliance Standard

> **Generated artifact warning:** `doc/FRGSYSTEM.md` is assembled output. Edit the
> source modules under `doc/system/` and rebuild. Hand edits to the compiled
> artifact are overwritten by the next build.

Assembly contract:

- Command: `bash doc/system/BUILD.sh`
- Validation: `bash doc/system/validate_snapshots.sh` runs during assembly
- Primary output: `doc/FRGSYSTEM.md`

This `doc/system/` tree is the canonical source of truth for forgeHQ. It uses
explicit **truth classes**: *canonical facts* define the proposal-shaping role,
artifact model, pipeline/reviewability contract, signal-intake boundaries, and
ecosystem contracts; *snapshot facts* are dated, audit-derived counts (routes,
tables, tests). forgeHQ is non-authoritative — it proposes and evaluates
candidates; it does not mint canonical truth. See §15 for the scope/authority
boundary and §16 for ownership and designation doctrine.

| Part | File | Contents |
| --- | --- | --- |
| §1 | `00_overview/01-overview-philosophy.md` | Service identity, proposal-shaping role |
| §2 | `00_overview/02-architecture.md` | Architecture overview |
| §3 | `00_overview/03-project-structure.md` | Repository tree, module layout |
| §4 | `10_service-contract/04-design-system.md` | Design system, brand tokens |
| §5 | `10_service-contract/05-frontend.md` | Frontend routes/components |
| §6 | `10_service-contract/06-api-layer.md` | API endpoints, auth |
| §7 | `10_service-contract/07-proposal-artifact-model.md` | The shaped-proposal artifact model |
| §8 | `10_service-contract/08-pipeline-reviewability.md` | Signal→proposal pipeline + reviewability contract |
| §9 | `20_runtime/09-backend.md` | Backend services |
| §10 | `20_runtime/10-database-schema.md` | Tables, migrations |
| §11 | `20_runtime/11-ai-integration.md` | AI integration |
| §12 | `20_runtime/12-error-handling.md` | Error handling contract |
| §13 | `30_dependencies/13-tech-stack.md` | Dependencies, versions |
| §14 | `30_dependencies/14-ecosystem-integration.md` | Feeder + ecosystem contracts |
| §15 | `40_governance/15-scope.md` | Service authority boundary, truth classes |
| §16 | `40_governance/16-governance.md` | Ownership, designation doctrine, authority hierarchy |
| §17 | `40_governance/17-change-control.md` | Change classes, evidence, verification commands |
| §18 | `50_operations/18-configuration.md` | Configuration and environment variables |
| §19 | `50_operations/19-testing-infrastructure.md` | Testing posture |
| §20 | `50_operations/20-handover-migration-notes.md` | Handover / migration notes |
| §21 | `99_appendices/21-appendices.md` | Glossary, cross-references, revision history |

## Quick Assembly

```bash
bash doc/system/BUILD.sh
```
