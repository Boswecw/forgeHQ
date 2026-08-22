"""FMHQ-02: disabled, fixture-only memory candidate projection."""

from copy import deepcopy
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path

import pytest

from app.domain.artifacts.enums import ArtifactAuthorityPosture
from app.services.memory_skill_candidate_fixture_adapter import (
    FCC_SOURCE_COMMIT,
    FixtureAdapterDisabledError,
    FixtureObservationContext,
    MemorySkillCandidateFixtureAdapter,
    MemorySkillCandidateFixtureError,
)


FIXTURE = (
    Path(__file__).parents[1]
    / "fixtures"
    / "fcc"
    / "memory_skill_candidate.v1.valid.json"
)


def candidate() -> dict:
    value = json.loads(FIXTURE.read_text(encoding="utf-8"))
    value.pop("_fixture")
    return value


def context(**changes) -> FixtureObservationContext:
    value = candidate()
    payload = value["payload"]
    resolved = {payload["subject"]["artifact_ref"]}
    for row in payload["evidence"]:
        resolved.add(row["use_receipt_ref"])
        resolved.add(row["retrieval_receipt_ref"])
    fields = {
        "observed_at": datetime(2026, 8, 22, 10, tzinfo=timezone.utc),
        "max_candidate_age": timedelta(hours=2),
        "subject_current": True,
        "subject_eligible": True,
        "resolved_refs": frozenset(resolved),
    }
    fields.update(changes)
    return FixtureObservationContext(**fields)


def adapt(value: dict | None = None, ctx: FixtureObservationContext | None = None):
    return MemorySkillCandidateFixtureAdapter(enabled=True).adapt(
        run_id="fixture-run",
        artifact=value or candidate(),
        context=ctx or context(),
    )


def test_adapter_is_disabled_by_default():
    with pytest.raises(FixtureAdapterDisabledError):
        MemorySkillCandidateFixtureAdapter().adapt(
            run_id="fixture-run", artifact=candidate(), context=context()
        )


def test_exact_fcc_fixture_projects_to_existing_weak_signal_lane():
    result = adapt()
    assert result.signal_snapshot.source_refs == (
        "signal://memory_skill_candidate/c1f2a3b4-0001-4000-8000-000000000001",
    )
    assert result.signal_snapshot.authority_posture == ArtifactAuthorityPosture.NON_AUTHORITATIVE
    assert result.proposal_context.source_contract_commit == FCC_SOURCE_COMMIT
    assert result.proposal_context.overrides_recorded == 1
    assert len(result.proposal_context.evidence) == 3
    assert result.proposal_context.evidence[0].decision_ref == "dec-101"


def test_projection_is_deterministic_and_preserves_counter_evidence():
    first = adapt().proposal_context
    second = adapt().proposal_context
    assert first == second
    assert first.canonical_sha256 == second.canonical_sha256
    assert first.independent_successes == 3
    assert first.distinct_consumers == 2
    assert first.overrides_recorded == 1


@pytest.mark.parametrize(
    "field,value",
    [
        ("artifact_family", "memory_fact"),
        ("artifact_version", 2),
        ("produced_by_system", "forgeHQ"),
        ("source_scope", "shared"),
        ("promotion_class", "promotable"),
    ],
)
def test_wrong_envelope_identity_or_local_only_posture_is_refused(field, value):
    value_under_test = candidate()
    value_under_test[field] = value
    with pytest.raises(MemorySkillCandidateFixtureError):
        adapt(value_under_test)


@pytest.mark.parametrize(
    "field,value",
    [
        ("lineage_root_id", "not-a-uuid"),
        ("idempotency_key", "0" * 63),
        ("created_at", "yesterday"),
        ("recorded_at", "2026-08-22T09:14:59Z"),
        ("sensitivity_class", "restricted"),
        ("visibility_class", "internal"),
        ("signer_identity", "somebody-else"),
    ],
)
def test_malformed_envelope_provenance_is_refused(field, value):
    value_under_test = candidate()
    value_under_test[field] = value
    with pytest.raises(MemorySkillCandidateFixtureError):
        adapt(value_under_test)


def test_extra_contract_field_is_refused():
    value = candidate()
    value["payload"]["verdict"] = "yes"
    with pytest.raises(MemorySkillCandidateFixtureError, match="extra"):
        adapt(value)


def test_duplicate_supply_event_is_refused():
    value = candidate()
    value["payload"]["evidence"][1]["retrieval_receipt_ref"] = "rr-01"
    with pytest.raises(MemorySkillCandidateFixtureError, match="repeats a retrieval"):
        adapt(value)


def test_duplicate_non_null_decision_is_refused():
    value = candidate()
    value["payload"]["evidence"][1]["decision_ref"] = "dec-101"
    with pytest.raises(MemorySkillCandidateFixtureError, match="repeats a non-null decision"):
        adapt(value)


def test_claimed_counts_must_match_evidence_and_consumers():
    count_mismatch = candidate()
    count_mismatch["payload"]["counts"]["independent_successes"] = 4
    with pytest.raises(MemorySkillCandidateFixtureError, match="evidence length"):
        adapt(count_mismatch)

    consumer_mismatch = candidate()
    consumer_mismatch["payload"]["counts"]["distinct_consumers"] = 3
    with pytest.raises(MemorySkillCandidateFixtureError, match="disagrees with evidence"):
        adapt(consumer_mismatch)


def test_candidate_must_meet_its_stated_policy():
    value = candidate()
    value["payload"]["policy_applied"]["min_independent_successes"] = 4
    with pytest.raises(MemorySkillCandidateFixtureError, match="stated policy"):
        adapt(value)


def test_stale_or_future_candidate_is_refused():
    with pytest.raises(MemorySkillCandidateFixtureError, match="stale"):
        adapt(ctx=context(observed_at=datetime(2026, 8, 23, tzinfo=timezone.utc)))

    future = candidate()
    future["payload"]["proposed_at"] = "2026-08-22T11:00:00Z"
    with pytest.raises(MemorySkillCandidateFixtureError, match="future"):
        adapt(future)


@pytest.mark.parametrize(
    "changes,reason",
    [
        ({"subject_current": False}, "not current"),
        ({"subject_eligible": False}, "ineligible or poisoned"),
        ({"resolved_refs": frozenset()}, "unresolvable"),
    ],
)
def test_external_current_eligibility_and_resolution_gates_fail_closed(changes, reason):
    with pytest.raises(MemorySkillCandidateFixtureError, match=reason):
        adapt(ctx=context(**changes))


def test_malformed_identifiers_and_timestamps_are_refused():
    bad_id = candidate()
    bad_id["payload"]["skill_candidate_id"] = "not-a-uuid"
    with pytest.raises(MemorySkillCandidateFixtureError, match="UUID"):
        adapt(bad_id)

    bad_time = candidate()
    bad_time["payload"]["proposed_at"] = "yesterday"
    with pytest.raises(MemorySkillCandidateFixtureError, match="RFC 3339"):
        adapt(bad_time)


def test_input_is_not_mutated():
    value = candidate()
    before = deepcopy(value)
    adapt(value)
    assert value == before
