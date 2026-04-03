# forgeHQ QA Run Report Template

## Run Metadata

| Field | Value |
| --- | --- |
| Run ID | `FORGEHQ-QA-YYYYMMDD-01` |
| Date | |
| Operator | |
| Branch | |
| Commit | |
| Mode | `Mode A` or `Mode B` |
| Repo maturity | `contract/bootstrap repo with a Phase 1 scaffold` |

## Tier Applicability

| Tier | Status | Notes |
| --- | --- | --- |
| T0 | applicable now | |
| T1 | applicable now | |
| T2 | not applicable yet | no UI exists |
| T3 | not applicable yet | no API exists |
| T4 | not applicable yet | no live runtime exists |
| T5 | not applicable yet | no end-to-end runtime exists |
| T6 | limited applicability now | tooling-response checks only |
| T7 | not applicable yet | no packaging targets exist |
| T8 | not applicable yet | no UI exists |

## Commands Executed

| Step | Command | Result | Duration |
| --- | --- | --- | --- |
| 1 | `bash doc/system/BUILD.sh` | | |
| 2 | `bash scripts/context-bundle.sh --list` | | |
| 3 | `bash scripts/context-bundle.sh --dry-run --preset core --with-roadmap` | | |
| 4 | `bash scripts/qa-regression-smoke.sh` | | |
| 5 | `pytest` full suite | | |

## Findings Summary

| Severity | Count |
| --- | --- |
| S0 | |
| S1 | |
| S2 | |
| S3 | |
| S4 | |

Reference the detailed findings log generated from `FORGEHQ_QA_FINDINGS_LOG_TEMPLATE.md`.

## Gate Decision

| Decision | Rationale |
| --- | --- |
| `pass` / `conditional` / `fail` | |
