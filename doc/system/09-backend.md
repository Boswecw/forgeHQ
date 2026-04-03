## 9. Backend

The backend currently consists of domain-contract modules,
typed schema stubs, a strict stage router, and a no-op orchestrator.
No live service runtime or persistence layer has been implemented yet.

### 9.1 Current Backend Modules

| Module | Files | Current responsibility |
| --- | --- | --- |
| Artifact domain | `app/domain/artifacts/enums.py` | Artifact families, lineage layers, backbone registry |
| Pipeline domain | `app/domain/pipeline/enums.py` | Stage order, stage artifacts, stage owners |
| Reviewability domain | `app/domain/reviewability/enums.py` | Reviewability requirements, lifecycle state split, language posture |
| Worker domain | `app/domain/workers/enums.py` | Worker identities and allowed emissions |
| Schema stubs | `app/schemas/` | Typed placeholders for shaping runs and required artifacts |
| Stage router | `app/orchestration/stage_router.py` | Fail-closed stage-order and predecessor validation |
| No-op orchestrator | `app/orchestration/forgehq_orchestrator.py` | Placeholder artifact emission in strict stage order |

### 9.2 Current Missing Backend Slices

| Slice | Status |
| --- | --- |
| `app/services/` | Not implemented |
| `app/persistence/` | Not implemented |
| `app/read_models/` | Not implemented |

### 9.3 Backend Law

Current backend code exists to lock repo semantics before live service logic arrives.
The orchestrator is a bounded scaffold for placeholder progression, not production execution semantics.
