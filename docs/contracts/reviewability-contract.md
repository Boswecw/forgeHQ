# Reviewability Contract

A forgeHQ proposal may only be `reviewable` when all required backbone artifacts exist and every hard gate below passes.

## Required reviewability conditions

- design present
- candidate present
- challenge present
- verification present
- non-authoritative notice present
- explicit scope boundary statement present
- parent refs valid
- no unresolved scope escape
- no broken lineage condition

## Automatic `not_reviewable` conditions

- missing challenge artifact
- missing verification artifact
- missing source refs
- scope escape detected
- invalid parent evidence refs
- confidence summary missing downgrade factors
- rollback class required but absent

## State-separation rule

Proposal lifecycle state is forgeHQ workflow state.

Operator decision state is downstream human action state.

These state families must never be collapsed into a single enum or field.
