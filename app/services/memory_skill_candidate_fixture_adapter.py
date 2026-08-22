"""Disabled-by-default fixture adapter for ``memory_skill_candidate`` v1.

This module is an offline proving surface, not a consumer admission.  It has no
transport, persistence, API, command, or promotion hook.  A test must opt in at
construction time and supply the observation context needed to fail closed on
stale, ineligible, non-current, or unresolvable evidence.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from hashlib import sha256
import json
import re
from typing import Any, Mapping
from uuid import UUID

from app.schemas.intake_diagnostics import IntakeDiagnostics
from app.schemas.signal_snapshot import SignalSnapshot
from app.services.signal_intake_service import SignalIntakeService


FCC_SOURCE_COMMIT = "a04c63cf5c6359237efc75410b3db122465b6e8b"
FAMILY = "memory_skill_candidate"
SCHEMA_VERSION = "forge.memory_skill_candidate.v1"
_REF = re.compile(r"^[a-z0-9_]+:[^:]+:v[0-9]+$")
_WEIGHTS = frozenset({"decisive", "contributing", "background"})


class MemorySkillCandidateFixtureError(ValueError):
    """The fixture adapter refused an input without admitting it."""


class FixtureAdapterDisabledError(MemorySkillCandidateFixtureError):
    """The explicitly disabled boundary was invoked."""


@dataclass(frozen=True, slots=True)
class FixtureObservationContext:
    """Test-owned facts that are intentionally absent from the candidate."""

    observed_at: datetime
    max_candidate_age: timedelta
    subject_current: bool
    subject_eligible: bool
    resolved_refs: frozenset[str]

    def __post_init__(self) -> None:
        if self.observed_at.tzinfo is None:
            raise ValueError("observed_at must be timezone-aware")
        if self.max_candidate_age <= timedelta(0):
            raise ValueError("max_candidate_age must be positive")


@dataclass(frozen=True, slots=True)
class CandidateScope:
    tenant_id: str
    user_id: str | None
    project_id: str | None
    repo_id: str | None


@dataclass(frozen=True, slots=True)
class CandidateSubject:
    artifact_ref: str
    memory_id: str


@dataclass(frozen=True, slots=True)
class CandidateEvidence:
    use_receipt_ref: str
    retrieval_receipt_ref: str
    consumer: str
    decision_ref: str | None
    causal_weight: str


@dataclass(frozen=True, slots=True)
class CandidateProposalContext:
    """Immutable context retained beside the weak signal projection."""

    source_contract_commit: str
    source_artifact_id: str
    skill_candidate_id: str
    proposed_at: datetime
    scope: CandidateScope
    subject: CandidateSubject
    min_independent_successes: int
    min_distinct_consumers: int
    independent_successes: int
    distinct_consumers: int
    overrides_recorded: int
    evidence: tuple[CandidateEvidence, ...]
    consolidation_ref: str | None
    canonical_sha256: str


@dataclass(frozen=True, slots=True)
class MemorySkillCandidateFixtureIntake:
    """Non-authoritative pipeline input plus the evidence it must not erase."""

    signal_snapshot: SignalSnapshot
    intake_diagnostics: IntakeDiagnostics
    proposal_context: CandidateProposalContext


class MemorySkillCandidateFixtureAdapter:
    """Validate one FCC fixture and project it into the existing weak-signal lane."""

    def __init__(self, *, enabled: bool = False) -> None:
        self._enabled = enabled

    def adapt(
        self,
        *,
        run_id: str,
        artifact: Mapping[str, Any],
        context: FixtureObservationContext,
    ) -> MemorySkillCandidateFixtureIntake:
        if not self._enabled:
            raise FixtureAdapterDisabledError(
                "memory skill candidate fixture adapter is disabled"
            )

        proposal_context = _validate(artifact, context)
        source_ref = f"signal://memory_skill_candidate/{proposal_context.skill_candidate_id}"
        snapshot, diagnostics = SignalIntakeService().admit_signals(
            run_id=run_id,
            source_refs=(source_ref,),
        )
        return MemorySkillCandidateFixtureIntake(
            signal_snapshot=snapshot,
            intake_diagnostics=diagnostics,
            proposal_context=proposal_context,
        )


def _validate(
    artifact: Mapping[str, Any], context: FixtureObservationContext
) -> CandidateProposalContext:
    _exact_keys(
        artifact,
        required={
            "artifact_id", "artifact_family", "artifact_version",
            "produced_by_system", "produced_by_component", "source_scope",
            "lineage_root_id", "parent_artifact_id", "trace_id",
            "idempotency_key", "created_at", "recorded_at",
            "sensitivity_class", "visibility_class", "promotion_class",
            "validation_status", "signer_identity", "signature", "payload",
        },
        where="envelope",
    )
    if artifact["artifact_family"] != FAMILY or artifact["artifact_version"] != 1:
        _refuse("family/version does not match memory_skill_candidate v1")
    if artifact["produced_by_system"] != "forge-memory":
        _refuse("candidate producer must be forge-memory")
    if artifact["produced_by_component"] != "consolidation":
        _refuse("candidate component must be consolidation")
    if artifact["source_scope"] != "local" or artifact["promotion_class"] != "local_only":
        _refuse("fixture candidate must remain local-only")
    if artifact["validation_status"] != "valid":
        _refuse("fixture candidate must carry validation_status=valid")
    _uuid(artifact["artifact_id"], "artifact_id")

    payload = _mapping(artifact["payload"], "payload")
    _exact_keys(
        payload,
        required={
            "schema_version", "skill_candidate_id", "proposed_at", "scope",
            "subject", "policy_applied", "evidence", "counts",
        },
        optional={"consolidation_ref"},
        where="payload",
    )
    if payload["schema_version"] != SCHEMA_VERSION:
        _refuse("payload schema_version mismatch")
    candidate_id = _uuid(payload["skill_candidate_id"], "skill_candidate_id")
    proposed_at = _timestamp(payload["proposed_at"], "proposed_at")
    observed_at = context.observed_at.astimezone(timezone.utc)
    if proposed_at > observed_at:
        _refuse("candidate proposed_at is in the future")
    if observed_at - proposed_at > context.max_candidate_age:
        _refuse("candidate is stale")
    if not context.subject_current:
        _refuse("candidate subject is not current")
    if not context.subject_eligible:
        _refuse("candidate subject is ineligible or poisoned")

    scope_raw = _mapping(payload["scope"], "scope")
    _exact_keys(
        scope_raw,
        required={"tenant_id"},
        optional={"user_id", "project_id", "repo_id"},
        where="scope",
    )
    scope = CandidateScope(
        tenant_id=_bounded_text(scope_raw["tenant_id"], "scope.tenant_id", 128),
        user_id=_nullable_text(scope_raw.get("user_id"), "scope.user_id", 128),
        project_id=_nullable_text(scope_raw.get("project_id"), "scope.project_id", 128),
        repo_id=_nullable_text(scope_raw.get("repo_id"), "scope.repo_id", 128),
    )

    subject_raw = _mapping(payload["subject"], "subject")
    _exact_keys(subject_raw, required={"artifact_ref", "memory_id"}, where="subject")
    subject = CandidateSubject(
        artifact_ref=_bounded_text(subject_raw["artifact_ref"], "subject.artifact_ref", 512),
        memory_id=_bounded_text(subject_raw["memory_id"], "subject.memory_id", 512),
    )
    if not _REF.fullmatch(subject.artifact_ref):
        _refuse("subject.artifact_ref does not match canonical reference grammar")

    policy = _mapping(payload["policy_applied"], "policy_applied")
    _exact_keys(
        policy,
        required={"min_independent_successes", "min_distinct_consumers"},
        where="policy_applied",
    )
    min_successes = _integer(policy["min_independent_successes"], 2, 1_000_000, "policy successes")
    min_consumers = _integer(policy["min_distinct_consumers"], 1, 1_000_000, "policy consumers")

    evidence_raw = payload["evidence"]
    if not isinstance(evidence_raw, list) or not 2 <= len(evidence_raw) <= 1000:
        _refuse("evidence must contain between 2 and 1000 entries")
    evidence: list[CandidateEvidence] = []
    for index, item in enumerate(evidence_raw):
        row = _mapping(item, f"evidence[{index}]")
        _exact_keys(
            row,
            required={
                "use_receipt_ref", "retrieval_receipt_ref", "consumer",
                "decision_ref", "causal_weight",
            },
            where=f"evidence[{index}]",
        )
        weight = row["causal_weight"]
        if weight not in _WEIGHTS:
            _refuse(f"evidence[{index}].causal_weight is invalid")
        evidence.append(
            CandidateEvidence(
                use_receipt_ref=_bounded_text(row["use_receipt_ref"], "use receipt ref", 512),
                retrieval_receipt_ref=_bounded_text(row["retrieval_receipt_ref"], "retrieval receipt ref", 512),
                consumer=_bounded_text(row["consumer"], "consumer", 256),
                decision_ref=_nullable_text(row["decision_ref"], "decision_ref", 512),
                causal_weight=weight,
            )
        )

    retrieval_refs = [row.retrieval_receipt_ref for row in evidence]
    if len(set(retrieval_refs)) != len(retrieval_refs):
        _refuse("evidence repeats a retrieval receipt")
    decision_refs = [row.decision_ref for row in evidence if row.decision_ref is not None]
    if len(set(decision_refs)) != len(decision_refs):
        _refuse("evidence repeats a non-null decision")

    counts = _mapping(payload["counts"], "counts")
    _exact_keys(
        counts,
        required={"independent_successes", "distinct_consumers", "overrides_recorded"},
        where="counts",
    )
    independent_successes = _integer(counts["independent_successes"], 2, 1_000_000, "independent successes")
    distinct_consumers = _integer(counts["distinct_consumers"], 1, 1_000_000, "distinct consumers")
    overrides_recorded = _integer(counts["overrides_recorded"], 0, 1_000_000, "overrides recorded")
    if independent_successes != len(evidence):
        _refuse("independent_successes disagrees with evidence length")
    if distinct_consumers != len({row.consumer for row in evidence}):
        _refuse("distinct_consumers disagrees with evidence")
    if independent_successes < min_successes or distinct_consumers < min_consumers:
        _refuse("candidate does not meet its stated policy")

    consolidation_ref = _nullable_text(payload.get("consolidation_ref"), "consolidation_ref", 512)
    required_refs = {subject.artifact_ref}
    for row in evidence:
        required_refs.add(row.use_receipt_ref)
        required_refs.add(row.retrieval_receipt_ref)
    if not required_refs.issubset(context.resolved_refs):
        missing = sorted(required_refs - context.resolved_refs)
        _refuse(f"candidate evidence is unresolvable: {missing}")

    canonical = json.dumps(artifact, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return CandidateProposalContext(
        source_contract_commit=FCC_SOURCE_COMMIT,
        source_artifact_id=str(artifact["artifact_id"]),
        skill_candidate_id=candidate_id,
        proposed_at=proposed_at,
        scope=scope,
        subject=subject,
        min_independent_successes=min_successes,
        min_distinct_consumers=min_consumers,
        independent_successes=independent_successes,
        distinct_consumers=distinct_consumers,
        overrides_recorded=overrides_recorded,
        evidence=tuple(evidence),
        consolidation_ref=consolidation_ref,
        canonical_sha256=sha256(canonical.encode("utf-8")).hexdigest(),
    )


def _exact_keys(
    value: Mapping[str, Any], *, required: set[str], where: str, optional: set[str] | None = None
) -> None:
    keys = set(value)
    allowed = required | (optional or set())
    if keys != required and not (required.issubset(keys) and keys.issubset(allowed)):
        _refuse(f"{where} keys mismatch: missing={sorted(required - keys)}, extra={sorted(keys - allowed)}")


def _mapping(value: Any, where: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        _refuse(f"{where} must be an object")
    return value


def _bounded_text(value: Any, where: str, maximum: int) -> str:
    if not isinstance(value, str) or not 1 <= len(value) <= maximum:
        _refuse(f"{where} must be a non-empty string of at most {maximum} characters")
    return value


def _nullable_text(value: Any, where: str, maximum: int) -> str | None:
    if value is None:
        return None
    return _bounded_text(value, where, maximum)


def _integer(value: Any, minimum: int, maximum: int, where: str) -> int:
    if type(value) is not int or not minimum <= value <= maximum:
        _refuse(f"{where} must be an integer from {minimum} through {maximum}")
    return value


def _uuid(value: Any, where: str) -> str:
    text = _bounded_text(value, where, 64)
    try:
        UUID(text)
    except ValueError as exc:
        raise MemorySkillCandidateFixtureError(f"{where} must be a UUID") from exc
    return text


def _timestamp(value: Any, where: str) -> datetime:
    text = _bounded_text(value, where, 64)
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError as exc:
        raise MemorySkillCandidateFixtureError(f"{where} must be RFC 3339") from exc
    if parsed.tzinfo is None:
        _refuse(f"{where} must include a timezone")
    return parsed.astimezone(timezone.utc)


def _refuse(message: str) -> None:
    raise MemorySkillCandidateFixtureError(message)
