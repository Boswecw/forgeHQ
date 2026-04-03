# Artifact Family Registry

Every forgeHQ artifact family is non-authoritative by default and must remain bounded to the forgeHQ role.

| Artifact family | Stage | Owner | Required for reviewability backbone | Purpose |
| --- | --- | --- | --- | --- |
| `signal_snapshot` | `signal_intake` | `signal_analyst` | yes | Preserve admitted source signals and source refs. |
| `intake_diagnostics` | `signal_intake` | `signal_analyst` | no | Preserve fail-closed intake diagnostics. |
| `target_ranking` | `target_ranking` | `signal_analyst` | yes | Preserve why one target surfaced. |
| `ranking_factor_trace` | `target_ranking` | `signal_analyst` | no | Preserve explainability for ranking factors. |
| `context_bundle` | `context_curation` | `context_curator` | yes | Preserve bounded single-target context and scope statement. |
| `candidate_design` | `candidate_design` | `designer` | yes | Preserve the bounded change hypothesis before generation. |
| `candidate_patch` | `candidate_generation` | `generator` | yes | Preserve bounded generated change content. |
| `falsification_report` | `falsification` | `critic_falsifier` | yes | Preserve independent challenge posture. |
| `candidate_verification` | `verification` | `verifier` | yes | Preserve observed gain and residual weakness. |
| `confidence_shaping_summary` | `proposal_packaging` | `proposal_assembler` | yes | Preserve non-authoritative confidence language. |
| `forgehq_proposal` | `proposal_packaging` | `proposal_assembler` | yes | Preserve the review package for human operators. |
| `forgehq_evidence_bundle` | `proposal_packaging` | `proposal_assembler` | no | Optional supporting bundle for review surfaces. |

## Worker boundary rules

- Each worker may emit only the artifact families assigned to that worker.
- The orchestrator sequences stages but emits no proposal content.
- The critic/falsifier lane must stay structurally independent from the generator lane.
- Missing required backbone artifacts force `not_reviewable`.
