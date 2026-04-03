# forgeHQ Mode A T0 Checklist

**Mode:** A (Monorepo / local-only)  
**Repo maturity:** contract/bootstrap repo with a Phase 1 scaffold, not a live shaping service

## Required Checks

- [ ] `bash doc/system/BUILD.sh` succeeds and reports `SYSTEM.md assembled`
- [ ] `bash scripts/context-bundle.sh --list` succeeds and prints available sections and presets
- [ ] `bash scripts/context-bundle.sh --dry-run --preset core --with-roadmap` succeeds
- [ ] a pytest runner is discoverable through `PYTEST_RUNNER`, `./.venv/bin/pytest`, `../DataForge/.venv/bin/pytest`, or `python3 -m pytest`
- [ ] the repo test suite passes with the selected runner

## Mode A Boundaries

- No UI, API, database, or external-service boot checks are expected yet.
- Database migration checks are deferred because forgeHQ has no persistence layer.
- Cross-service proxy checks are deferred because forgeHQ has no live runtime services.

## Findings Handling

- Record every failure in `FORGEHQ_QA_FINDINGS_LOG_TEMPLATE.md` format.
- Do not proceed past T0 with unresolved S0 or S1 findings.
