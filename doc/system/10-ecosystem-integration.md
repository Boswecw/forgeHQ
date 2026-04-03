## 10. Ecosystem Integration

forgeHQ exists inside a larger BDS ecosystem but currently ships only declared boundaries rather than live adapters.

### 10.1 Boundary Table

| System | Relationship | Current status |
| --- | --- | --- |
| ForgeEval | Upstream evidence substrate | Declared boundary only |
| ForgeMath | Upstream math/rule authority where adopted | Declared boundary only |
| DataForge | Downstream persistence, lineage, rollback linkage | Declared boundary only |
| ForgeCommand | Downstream review surface and operator action state | Declared boundary only |

### 10.2 Integration Laws

- forgeHQ may consume upstream artifacts but may not overwrite upstream truth
- forgeHQ proposals remain non-authoritative even after packaging
- operator action state belongs downstream and stays separate from proposal lifecycle state
