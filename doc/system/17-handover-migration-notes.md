## 17. Handover / Migration Notes

The current repo is a Phase 1 baseline.
It now includes a no-op shaping pipeline skeleton,
but it should not be misread as a functional shaping service yet.

### 17.1 Current Handover Summary

| Topic | Current truth |
| --- | --- |
| Repo maturity | Governance baseline plus Phase 1 stage scaffold |
| Runtime capability | No-op stage progression with placeholder artifacts only |
| Canonical documentation source | `doc/system/` |
| Root build artifact | `SYSTEM.md` |
| Root QA plan | `FORGEHQ_COMPREHENSIVE_TEST_PLAN.md` |
| QA support docs | `docs/qa/` |
| QA executable entrypoints | `scripts/qa-mode-a-preflight.sh`, `scripts/qa-regression-smoke.sh` |
| Selective context source | `scripts/context-bundle.sh` |
| Imported ecosystem doctrine | `docs/reference/bds/` |

### 17.2 Migration Notes

- existing governance docs in `docs/` remain valid source material and are now reflected in the assembled system reference
- company-core protocols are stored as imported references under `docs/reference/bds/`, not as ambiguous repo-root files
- QA protocol compliance for current maturity now lives in the root test plan plus `docs/qa/` support artifacts
- future service slices must update both `docs/` and `doc/system/` when repo truth changes
- repo-local Phase 1 implementation and QA foundation are complete enough to support bounded Phase 2 work
