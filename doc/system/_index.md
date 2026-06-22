        # forgeHQ - Compiled System Reference

        **Designation:** FRG
        **Document role:** Canonical compiled technical reference for forgeHQ
        **Source:** `doc/system/`
        **Build command:** `bash doc/system/BUILD.sh`
        **Document version:** 2.0 (2026-06-22) - canonical compliance migration
        **Protocol:** BDS Documentation Protocol v2.0; BDS Repo Documentation System Canonical Compliance Standard

        > **Generated artifact warning:** `doc/FRGSYSTEM.md` is assembled output. Edit
        > the source modules under `doc/system/` and rebuild. Hand edits to the
        > compiled artifact are overwritten by the next build.

        Assembly contract:

        - Command: `bash doc/system/BUILD.sh`
        - Validation: `bash doc/system/validate_snapshots.sh` runs during assembly
        - Primary output: `doc/FRGSYSTEM.md`

        This `doc/system/` tree is the canonical source of truth for forgeHQ. It uses
        explicit **truth classes**: canonical facts define repo role, authority
        boundaries, contract behavior, runtime behavior, and verification doctrine;
        snapshot facts are dated, audit-derived counts and current implementation
        inventory that may drift between audits.

        | Part | File | Contents |
        | --- | --- | --- |
        | §1 | `00_overview/00-overview.md` | Overview |
| §2 | `00_overview/01-architecture.md` | Architecture |
| §3 | `00_overview/01-overview-philosophy.md` | 1. Overview & Philosophy |
| §4 | `00_overview/02-architecture.md` | 2. Architecture |
| §5 | `00_overview/04-project-structure.md` | 4. Project Structure |
| §6 | `10_service-contract/08-api-layer.md` | 8. API Layer |
| §7 | `10_service-contract/10-ecosystem-integration.md` | 10. Ecosystem Integration |
| §8 | `10_service-contract/13-proposal-artifact-model.md` | 13. Proposal Artifact Model |
| §9 | `10_service-contract/14-pipeline-reviewability.md` | 14. Pipeline & Reviewability |
| §10 | `20_runtime/07-frontend.md` | 7. Frontend |
| §11 | `20_runtime/09-backend.md` | 9. Backend |
| §12 | `20_runtime/11-database-schema.md` | 11. Database Schema |
| §13 | `20_runtime/12-ai-integration.md` | 12. AI Integration |
| §14 | `20_runtime/15-error-handling.md` | 15. Error Handling Contract |
| §15 | `30_dependencies/03-tech-stack.md` | 3. Tech Stack |
| §16 | `30_dependencies/06-design-system.md` | 6. Design System |
| §17 | `40_governance/10-scope.md` | Scope |
| §18 | `40_governance/30-governance.md` | Governance |
| §19 | `40_governance/40-change-control.md` | Change Control |
| §20 | `50_operations/05-configuration.md` | 5. Configuration & Environment |
| §21 | `50_operations/16-testing-infrastructure.md` | 16. Testing Infrastructure |
| §22 | `50_operations/17-handover-migration-notes.md` | 17. Handover / Migration Notes |
| §23 | `99_appendices/20-structure.md` | Structure |
| §24 | `99_appendices/90-appendices.md` | Appendices |

        ## Quick Assembly

        ```bash
        bash doc/system/BUILD.sh
        ```
