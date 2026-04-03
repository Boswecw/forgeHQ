# forgeHQ System Role

forgeHQ is the bounded proposal-generation and confidence-shaping subsystem for the BDS ecosystem.

## System role

forgeHQ may:
- consume ForgeEval evidence and ForgeMath outputs
- rank candidate improvement targets
- build bounded context for one target at a time
- design candidate changes before generation
- generate bounded candidate artifacts
- challenge those candidates through falsification
- verify candidate outcome
- package non-authoritative proposals for human review

forgeHQ may not:
- claim deterministic repo truth
- overwrite ForgeEval truth
- overwrite ForgeMath truth
- make approval decisions
- perform autonomous merges
- collapse proposal state into human decision state

## Boundary law

forgeHQ may consume upstream evidence, but it may not overwrite upstream systems as canonical truth.

Upstream dependencies:
- ForgeEval for deterministic evidence
- ForgeMath for canonical math and rule authority where adopted
- ecosystem signals for ranking, recurrence, exposure, and historical burden

Downstream dependencies:
- DataForge for persistence, lineage, rollback, and artifact references
- ForgeCommand for queue/detail review surfaces and recorded operator action state

## Governance posture

All forgeHQ artifacts must carry explicit non-authoritative posture.

Proposal lifecycle state must remain separate from operator decision state.

Ambiguity must fail closed rather than widening scope.
