# forgeHQ — System Documentation

**Document version:** 1.1 (2026-06-08) — full chapter set indexed
**Protocol:** Forge Documentation Protocol v1
**Documentation structure class:** `documentation`

This `doc/system/` tree is the canonical source of truth for forgeHQ.
Chapters are assembled into a designation-bound canonical artifact.

Assembly contract:

- Command: `bash doc/system/BUILD.sh`
- Validation: `bash doc/system/validate_snapshots.sh` runs during assembly
- Primary output: `doc/FRGSYSTEM.md`

## Table of Contents

0. [Overview](00-overview.md)
1. [Architecture](01-architecture.md)
1. [Overview Philosophy](01-overview-philosophy.md)
2. [Architecture](02-architecture.md)
3. [Tech Stack](03-tech-stack.md)
4. [Project Structure](04-project-structure.md)
5. [Configuration](05-configuration.md)
6. [Design System](06-design-system.md)
7. [Frontend](07-frontend.md)
8. [Api Layer](08-api-layer.md)
9. [Backend](09-backend.md)
10. [Ecosystem Integration](10-ecosystem-integration.md)
10. [Scope](10-scope.md)
11. [Database Schema](11-database-schema.md)
12. [AI Integration](12-ai-integration.md)
13. [Proposal Artifact Model](13-proposal-artifact-model.md)
14. [Pipeline Reviewability](14-pipeline-reviewability.md)
15. [Error Handling](15-error-handling.md)
16. [Testing Infrastructure](16-testing-infrastructure.md)
17. [Handover Migration Notes](17-handover-migration-notes.md)
20. [Structure](20-structure.md)
30. [Governance](30-governance.md)
40. [Change Control](40-change-control.md)
90. [Appendices](90-appendices.md)

## Quick Assembly

```bash
bash doc/system/BUILD.sh
```
