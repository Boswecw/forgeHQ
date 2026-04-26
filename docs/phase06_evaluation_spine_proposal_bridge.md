# ForgeHQ Phase 06 — Evaluation Spine Proposal Bridge

Date/Time: 2026-04-25

## Purpose

This slice adds the ForgeHQ-side bridge for the evaluation spine. ForgeHQ now has a bounded way to reference upstream evidence from:

1. Forge Eval evidence bundles
2. Eval Calibration reports
3. ForgeMath lane evaluation references

The bridge produces a ForgeHQ-owned `forgehq.upstream_evidence_refs.v1` payload that can later be attached to proposal candidates.

## Boundary

ForgeHQ remains non-authoritative.

This slice does not:

- recalculate Forge Eval scores,
- recalculate Eval Calibration normalization,
- recalculate ForgeMath canonical confidence or threshold decisions,
- approve operator action,
- execute remediation,
- become mathematical authority.

## Fail-Closed Rules

The bridge rejects upstream evidence when:

- Eval Calibration `validation_state` is not `passed`,
- ForgeMath `proposal_candidate_allowed` is not `true`,
- ForgeMath `rollback_required` is not `false`,
- the ForgeMath `source_artifact_hash` does not match the supplied Eval Calibration report hash,
- any required canonical artifact reference is malformed.

## Verification

Targeted test:

```bash
PYTHONPATH=. pytest -q tests/test_evaluation_spine_phase06_proposal_bridge.py
```

Full non-localization sweep:

```bash
PYTHONPATH=. pytest -q
```
