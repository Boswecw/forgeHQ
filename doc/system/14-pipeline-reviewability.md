## 14. Pipeline & Reviewability

The current repo implements the vocabulary for the shaping pipeline and reviewability gates,
plus a Phase 1 no-op router/orchestrator that can advance a shaping run with placeholder artifacts.
It still does not implement the live services behind those stages.

### 14.1 Stage Order

| Order | Stage | Primary owner |
| --- | --- | --- |
| 1 | `signal_intake` | `signal_analyst` |
| 2 | `target_ranking` | `signal_analyst` |
| 3 | `context_curation` | `context_curator` |
| 4 | `candidate_design` | `designer` |
| 5 | `candidate_generation` | `generator` |
| 6 | `falsification` | `critic_falsifier` |
| 7 | `verification` | `verifier` |
| 8 | `proposal_packaging` | `proposal_assembler` |

### 14.2 Reviewability Conditions

A proposal is reviewable only when all of the following are present:

- design
- candidate
- challenge
- verification
- non-authoritative notice
- explicit scope boundary statement
- valid parent refs
- no unresolved scope escape
- no broken lineage condition

### 14.3 Automatic Not-Reviewable Conditions

- missing challenge artifact
- missing verification artifact
- missing source refs
- scope escape detected
- invalid parent evidence refs
- confidence summary missing downgrade factors
- rollback class required but absent

### 14.4 Worker Boundary Law

- each worker emits only its admitted artifact families
- orchestrator emits no proposal content
- generator and critic/falsifier lanes remain structurally independent

### 14.5 Phase 1 Router Guarantees

- no stages may be skipped
- candidate generation is blocked when candidate design is missing
- proposal packaging is blocked when falsification is missing
- proposal packaging is blocked when verification is missing
- invalid run histories fail closed before artifact emission
