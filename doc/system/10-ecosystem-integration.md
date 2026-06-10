## 10. Ecosystem Integration

*Last updated: 2026-06-10 (producer entrypoint + NeuroForge model-learning edge)*

forgeHQ exists inside a larger BDS ecosystem. Upstream boundaries remain declared-only.
ForgeCommand now has implemented read models; the wire adapter is pending.
DataForge persistence uses in-memory stubs; the wire adapter is pending. The live
self-healing drivers (`learning_client`, `context_client`, `context_pack_publisher`,
`healing_publisher`) call NeuroForge / context-runtime / DataForge-Local directly.

### 10.1 Boundary Table

| System | Relationship | Current status |
| --- | --- | --- |
| ForgeEval | Upstream evidence substrate | Declared boundary; `forgeeval://` scheme admitted by `SignalIntakeService` |
| ForgeMath | Upstream math/rule authority where adopted | Declared boundary; `forgemath://` scheme admitted by `SignalIntakeService` |
| DataForge | Downstream persistence, lineage, rollback linkage | In-memory stubs implemented (`ArtifactRegistry`, `LineageRepository`, `ProposalRepository`); wire adapter pending |
| ForgeCommand | Downstream review surface and operator action state | Read models implemented; **also the producer trigger** — its self-healing tick spawns the `python -m app self-heal` entrypoint and injects the NeuroForge ingest key |
| NeuroForge | Downstream model-learning ingest (Category-Champion) | `learning_client` POSTs a `CodeFixOutcome` to `POST /api/v1/learning/model-outcome` (service-authenticated; fail-soft side-channel) |

### 10.2 Integration Laws

- forgeHQ may consume upstream artifacts but may not overwrite upstream truth
- forgeHQ proposals remain non-authoritative even after packaging
- operator action state belongs downstream and stays separate from proposal lifecycle state
- the learning emit is a non-authoritative side-channel: an ingest failure (down/401) is
  reported, never fatal to the propose path

### 10.3 Producer Entrypoint

`python -m app self-heal --repo <id> --repo-root <path> --target <file>` (see `app/cli.py`)
runs one fix end to end via `build_live_runner` — classify → governed context → publish
pack → generate (NeuroForge ladder, model captured) → pact-verify → emit `CodeFixOutcome`
→ propose — and prints a structured JSON result for the caller to capture as evidence. It
reads `NEUROFORGE_API_KEY` from the environment (ForgeCommand injects it at spawn, so the
secret never lands in a forgeHQ file). Exit codes: `0` ran (emit ok/skipped), `1` hard
failure (run raised), `3` ran but the learning emit failed (e.g. 401 ingest key).
