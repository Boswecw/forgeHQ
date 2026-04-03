## 2. Architecture

The current implementation is a contract-first Python repository.
It still does not expose an application runtime,
but it now includes a no-op shaping-run scaffold that can progress through all stages with placeholder artifacts.
Repo architecture is centered on bounded domain contracts, typed schema stubs,
strict stage routing, and a documentation assembly surface.

### 2.1 Current Implemented Shape

```text
forgeHQ/
  app/domain/artifacts/
  app/domain/pipeline/
  app/domain/reviewability/
  app/domain/workers/
  app/schemas/
  app/orchestration/
  docs/architecture/
  docs/contracts/
  doc/system/
  scripts/
  tests/
```

### 2.2 Boundary Diagram

```text
ForgeEval / ForgeMath
        |
        v
   forgeHQ contracts
        |
        v
DataForge / ForgeCommand
```

### 2.3 Architectural Posture

| Concern | Current posture |
| --- | --- |
| Upstream authority | Declared boundary only |
| Runtime orchestration | Implemented as a no-op stage scaffold only |
| Persistence boundary | Declared boundary only |
| Operator review surface | Declared boundary only |
| Repo documentation truth | Implemented via `doc/system/` and `SYSTEM.md` |

### 2.4 Hard Architectural Laws

- forgeHQ may consume upstream evidence but may not overwrite upstream canonical truth
- no proposal becomes reviewable without challenge and verification
- orchestrator sequencing may exist later, but orchestrator proposal authorship is forbidden
- reviewability posture must stay explicit, not inferred
