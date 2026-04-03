# forgeHQ QA Findings Log Template

Use this template for T0 through T8 findings. Severity follows the BugCheck S0-S4 model.

## Run Metadata

| Field | Value |
| --- | --- |
| Run ID | `FORGEHQ-QA-YYYYMMDD-01` |
| Mode | `Mode A` or `Mode B` |
| Branch | |
| Commit | |
| Operator | |

## Findings

| ID | Severity | Tier | Surface | Title | Reproduction | Status | Resolution / Rationale |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `FORGEHQ-T0-001` | `S1` | `T0` | `doc/system/BUILD.sh` | Example failure title | command and observed failure | `open` | fix applied or defer reason |

## Severity Notes

- `S0`: catastrophic blocker
- `S1`: critical blocker for the current tier
- `S2`: major but non-blocking with workaround
- `S3`: minor defect or edge case
- `S4`: enhancement suggestion
