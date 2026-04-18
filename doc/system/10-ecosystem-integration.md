## 10. Ecosystem Integration

*Last updated: 2026-04-04 (Phase 6: ForgeCommand read models implemented)*

forgeHQ exists inside a larger BDS ecosystem. Upstream boundaries remain declared-only.
ForgeCommand now has implemented read models; the wire adapter is pending.
DataForge persistence uses in-memory stubs; the wire adapter is pending.

### 10.1 Boundary Table

| System | Relationship | Current status |
| --- | --- | --- |
| ForgeEval | Upstream evidence substrate | Declared boundary; `forgeeval://` scheme admitted by `SignalIntakeService` |
| ForgeMath | Upstream math/rule authority where adopted | Declared boundary; `forgemath://` scheme admitted by `SignalIntakeService` |
| DataForge | Downstream persistence, lineage, rollback linkage | In-memory stubs implemented (`ArtifactRegistry`, `LineageRepository`, `ProposalRepository`); wire adapter pending |
| ForgeCommand | Downstream review surface and operator action state | Read models implemented (`ProposalQueueItem`, `ProposalDetailModel`, `ForgeCommandReadModelService`); HTTP API adapter pending |

### 10.2 Integration Laws

- forgeHQ may consume upstream artifacts but may not overwrite upstream truth
- forgeHQ proposals remain non-authoritative even after packaging
- operator action state belongs downstream and stays separate from proposal lifecycle state
