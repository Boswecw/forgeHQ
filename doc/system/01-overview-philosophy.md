## 1. Overview & Philosophy

forgeHQ is a backend/domain-contract repository for bounded proposal generation.
The current repo state implements the governance slice, the documentation stack,
and a Phase 1 no-op pipeline scaffold.
This repository defines how forgeHQ names artifacts, stages work,
separates proposal posture from decision posture,
and advances a shaping run through bounded placeholder artifacts without inventing live runtime semantics.

### 1.1 Core Principles

- forgeHQ is non-authoritative by design.
- Upstream truth remains with ForgeEval and ForgeMath where adopted.
- Human review remains downstream of forgeHQ proposals.
- Challenge and verification are mandatory before reviewability.
- Proposal lifecycle state never collapses into operator decision state.
- Ambiguity and scope escape fail closed.
- Documentation is part of repo truth, not a side artifact.

### 1.2 Current Product Boundary

| Area | Current status |
| --- | --- |
| Governance docs | Implemented |
| Artifact family registry | Implemented |
| Stage vocabulary | Implemented |
| Worker boundary registry | Implemented |
| Shaping run model | Implemented |
| Core artifact schema stubs | Implemented |
| Strict stage router | Implemented |
| No-op orchestrator skeleton | Implemented |
| Reviewability vocabulary | Implemented |
| Documentation assembly stack | Implemented |
| API surface | Not implemented |
| Live stage services | Not implemented |
| Persistence layer | Not implemented |
| Adapters and persistence wiring | Not implemented |
| UI or operator surface | Not implemented |
