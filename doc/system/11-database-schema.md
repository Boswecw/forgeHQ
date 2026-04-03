## 11. Database Schema

forgeHQ currently defines no database schema.
No migrations, tables, or repository persistence models exist in the current repo state.

### 11.1 Current Persistence Status

| Surface | Status |
| --- | --- |
| SQL migrations | Not implemented |
| ORM models | Not implemented |
| Artifact registry tables | Not implemented |
| Lineage edge tables | Not implemented |
| Proposal rows | Not implemented |

### 11.2 Future Boundary

When persistence is added later, DataForge-facing lineage and proposal persistence must preserve:

- deterministic evidence lineage
- non-authoritative proposal lineage
- operator decision linkage
