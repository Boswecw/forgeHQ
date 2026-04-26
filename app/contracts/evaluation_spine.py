"""Canonical evaluation-spine contract boundary for ForgeHQ.

ForgeHQ is a bounded proposal-shaping system. It may reference upstream
Forge Eval, Eval Calibration, and ForgeMath evidence, but it must not import
those repositories, recalculate their authority, or make operator decisions.

This module is intentionally narrow:
- validate canonical payload shapes at the boundary;
- expose the contract family/version names consumed by ForgeHQ;
- fail closed on malformed payloads;
- avoid direct imports from upstream implementation repos.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, Final


EVAL_CALIBRATION_REPORT_FAMILY: Final[str] = "eval_calibration_report"
FORGEMATH_LANE_EVALUATION_REF_FAMILY: Final[str] = "forgemath_lane_evaluation_ref"
FORGEHQ_UPSTREAM_EVIDENCE_REFS_FAMILY: Final[str] = "forgehq_upstream_evidence_refs"

EVAL_CALIBRATION_REPORT_SCHEMA_VERSION: Final[str] = "eval_cal_node.calibration_report.v1"
FORGEMATH_LANE_EVALUATION_REF_SCHEMA_VERSION: Final[str] = "forgemath.lane_evaluation_ref.v1"
FORGEHQ_UPSTREAM_EVIDENCE_REFS_SCHEMA_VERSION: Final[str] = "forgehq.upstream_evidence_refs.v1"

FORGEHQ_NON_AUTHORITATIVE_NOTICE: Final[str] = (
    "ForgeHQ may reference upstream evidence for proposal shaping but is not "
    "mathematical authority and is not operator decision authority."
)

FORGEMATH_NON_RECALCULATION_NOTICE: Final[str] = (
    "Downstream systems must reference this ForgeMath result and must not recalculate "
    "canonical confidence, band, threshold, proposal allowance, or rollback decision."
)

_ARTIFACT_REF_PATTERN: Final[re.Pattern[str]] = re.compile(
    r"^[a-z][a-z0-9_]*:[0-9a-fA-F-]{36}:v[1-9][0-9]*$"
)
_SHA256_PATTERN: Final[re.Pattern[str]] = re.compile(r"^sha256:[a-f0-9]{64}$")


class EvaluationSpineContractError(ValueError):
    """Raised when an evaluation-spine payload violates ForgeHQ's boundary."""


@dataclass(frozen=True)
class ContractValidationResult:
    """Small validation receipt used by ForgeHQ tests and services."""

    family: str
    schema_version: str
    validation_backend: str
    accepted: bool = True


def canonical_json_bytes(payload: Mapping[str, Any]) -> bytes:
    """Serialize a payload using deterministic JSON suitable for hashing."""

    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")


def compute_payload_hash(payload: Mapping[str, Any]) -> str:
    """Return the canonical sha256 digest for a payload."""

    return "sha256:" + hashlib.sha256(canonical_json_bytes(payload)).hexdigest()


def validate_eval_calibration_report_payload(payload: Mapping[str, Any]) -> ContractValidationResult:
    """Validate an Eval Calibration report consumed by ForgeHQ."""

    _validate_mapping(payload, EVAL_CALIBRATION_REPORT_FAMILY)
    _validate_eval_calibration_report_shape(payload)
    return ContractValidationResult(
        family=EVAL_CALIBRATION_REPORT_FAMILY,
        schema_version=EVAL_CALIBRATION_REPORT_SCHEMA_VERSION,
        validation_backend="forgehq_local_contract_boundary",
    )


def validate_forgemath_lane_evaluation_ref_payload(payload: Mapping[str, Any]) -> ContractValidationResult:
    """Validate the ForgeMath authority reference consumed by ForgeHQ."""

    _validate_mapping(payload, FORGEMATH_LANE_EVALUATION_REF_FAMILY)
    _validate_forgemath_lane_evaluation_ref_shape(payload)
    return ContractValidationResult(
        family=FORGEMATH_LANE_EVALUATION_REF_FAMILY,
        schema_version=FORGEMATH_LANE_EVALUATION_REF_SCHEMA_VERSION,
        validation_backend="forgehq_local_contract_boundary",
    )


def validate_forgehq_upstream_evidence_refs_payload(payload: Mapping[str, Any]) -> ContractValidationResult:
    """Validate the ForgeHQ upstream evidence reference bundle."""

    _validate_mapping(payload, FORGEHQ_UPSTREAM_EVIDENCE_REFS_FAMILY)
    _validate_forgehq_upstream_evidence_refs_shape(payload)
    return ContractValidationResult(
        family=FORGEHQ_UPSTREAM_EVIDENCE_REFS_FAMILY,
        schema_version=FORGEHQ_UPSTREAM_EVIDENCE_REFS_SCHEMA_VERSION,
        validation_backend="forgehq_local_contract_boundary",
    )


def _validate_mapping(payload: Mapping[str, Any], family: str) -> None:
    if not isinstance(payload, Mapping):
        raise EvaluationSpineContractError(f"{family} payload must be a mapping")


def _require_keys(payload: Mapping[str, Any], required: set[str], family: str) -> None:
    missing = sorted(required.difference(payload.keys()))
    if missing:
        raise EvaluationSpineContractError(f"{family} missing required keys: {', '.join(missing)}")


def _forbid_extra_keys(payload: Mapping[str, Any], allowed: set[str], family: str) -> None:
    extra = sorted(set(payload.keys()).difference(allowed))
    if extra:
        raise EvaluationSpineContractError(f"{family} contains unsupported keys: {', '.join(extra)}")


def _require_non_empty_string(value: Any, field: str, family: str, max_length: int = 256) -> None:
    if not isinstance(value, str) or not value or len(value) > max_length:
        raise EvaluationSpineContractError(f"{family}.{field} must be a non-empty string <= {max_length} chars")


def _require_artifact_ref(value: Any, field: str, family: str) -> None:
    if not isinstance(value, str) or not _ARTIFACT_REF_PATTERN.match(value):
        raise EvaluationSpineContractError(f"{family}.{field} must be a canonical artifact ref")


def _require_sha256(value: Any, field: str, family: str) -> None:
    if not isinstance(value, str) or not _SHA256_PATTERN.match(value):
        raise EvaluationSpineContractError(f"{family}.{field} must be a sha256:<64 lowercase hex> digest")


def _validate_eval_calibration_report_shape(payload: Mapping[str, Any]) -> None:
    family = EVAL_CALIBRATION_REPORT_FAMILY
    required = {
        "schema_version",
        "calibration_report_id",
        "source_forge_eval_evidence_bundle_ref",
        "source_artifact_hash",
        "repository_id",
        "score_normalization_version",
        "calibrated_scores",
        "confidence_band_candidate",
        "threshold_crossings",
        "validation_state",
    }
    allowed = required | {"normalization_notes"}
    _require_keys(payload, required, family)
    _forbid_extra_keys(payload, allowed, family)

    if payload["schema_version"] != EVAL_CALIBRATION_REPORT_SCHEMA_VERSION:
        raise EvaluationSpineContractError(f"{family}.schema_version is unsupported")
    _require_non_empty_string(payload["calibration_report_id"], "calibration_report_id", family)
    _require_artifact_ref(payload["source_forge_eval_evidence_bundle_ref"], "source_forge_eval_evidence_bundle_ref", family)
    _require_sha256(payload["source_artifact_hash"], "source_artifact_hash", family)
    _require_non_empty_string(payload["repository_id"], "repository_id", family)
    _require_non_empty_string(payload["score_normalization_version"], "score_normalization_version", family, 128)

    calibrated_scores = payload["calibrated_scores"]
    if not isinstance(calibrated_scores, list) or not 1 <= len(calibrated_scores) <= 50:
        raise EvaluationSpineContractError(f"{family}.calibrated_scores must contain 1..50 entries")
    for index, score in enumerate(calibrated_scores):
        if not isinstance(score, Mapping):
            raise EvaluationSpineContractError(f"{family}.calibrated_scores[{index}] must be a mapping")
        _require_keys(score, {"metric_name", "raw_score", "calibrated_score", "weight"}, family)
        _forbid_extra_keys(score, {"metric_name", "raw_score", "calibrated_score", "weight"}, family)
        _require_non_empty_string(score["metric_name"], f"calibrated_scores[{index}].metric_name", family, 128)
        if not isinstance(score["raw_score"], (int, float)) or isinstance(score["raw_score"], bool):
            raise EvaluationSpineContractError(f"{family}.calibrated_scores[{index}].raw_score must be numeric")
        if not isinstance(score["calibrated_score"], (int, float)) or not 0 <= score["calibrated_score"] <= 1:
            raise EvaluationSpineContractError(f"{family}.calibrated_scores[{index}].calibrated_score must be 0..1")
        if not isinstance(score["weight"], (int, float)) or not 0 <= score["weight"] <= 1:
            raise EvaluationSpineContractError(f"{family}.calibrated_scores[{index}].weight must be 0..1")

    if payload["confidence_band_candidate"] not in {"high_confidence", "medium_confidence", "low_confidence", "unknown"}:
        raise EvaluationSpineContractError(f"{family}.confidence_band_candidate is unsupported")

    threshold_crossings = payload["threshold_crossings"]
    if not isinstance(threshold_crossings, list) or len(threshold_crossings) > 20:
        raise EvaluationSpineContractError(f"{family}.threshold_crossings must contain <= 20 entries")
    for index, crossing in enumerate(threshold_crossings):
        if not isinstance(crossing, Mapping):
            raise EvaluationSpineContractError(f"{family}.threshold_crossings[{index}] must be a mapping")
        _require_keys(crossing, {"threshold_id", "crossed", "direction"}, family)
        _forbid_extra_keys(crossing, {"threshold_id", "crossed", "direction"}, family)
        _require_non_empty_string(crossing["threshold_id"], f"threshold_crossings[{index}].threshold_id", family, 128)
        if not isinstance(crossing["crossed"], bool):
            raise EvaluationSpineContractError(f"{family}.threshold_crossings[{index}].crossed must be boolean")
        if crossing["direction"] not in {"above", "below", "equal", "not_applicable"}:
            raise EvaluationSpineContractError(f"{family}.threshold_crossings[{index}].direction is unsupported")

    if payload["validation_state"] not in {"passed", "failed", "blocked"}:
        raise EvaluationSpineContractError(f"{family}.validation_state is unsupported")

    if "normalization_notes" in payload:
        notes = payload["normalization_notes"]
        if not isinstance(notes, list) or len(notes) > 20 or any(not isinstance(note, str) or len(note) > 512 for note in notes):
            raise EvaluationSpineContractError(f"{family}.normalization_notes must contain <= 20 strings <= 512 chars")


def _validate_forgemath_lane_evaluation_ref_shape(payload: Mapping[str, Any]) -> None:
    family = FORGEMATH_LANE_EVALUATION_REF_FAMILY
    required = {
        "schema_version",
        "lane_id",
        "lane_version",
        "source_eval_calibration_report_ref",
        "source_artifact_hash",
        "canonical_evaluation_ref",
        "canonical_score_ref",
        "threshold_decision_ref",
        "proposal_candidate_allowed",
        "rollback_required",
    }
    allowed = required | {"non_recalculation_notice"}
    _require_keys(payload, required, family)
    _forbid_extra_keys(payload, allowed, family)

    if payload["schema_version"] != FORGEMATH_LANE_EVALUATION_REF_SCHEMA_VERSION:
        raise EvaluationSpineContractError(f"{family}.schema_version is unsupported")
    if payload["lane_id"] != "self_healing_candidate_confidence_v1":
        raise EvaluationSpineContractError(f"{family}.lane_id is unsupported")
    if payload["lane_version"] != 1:
        raise EvaluationSpineContractError(f"{family}.lane_version is unsupported")
    _require_artifact_ref(payload["source_eval_calibration_report_ref"], "source_eval_calibration_report_ref", family)
    _require_sha256(payload["source_artifact_hash"], "source_artifact_hash", family)
    _require_non_empty_string(payload["canonical_evaluation_ref"], "canonical_evaluation_ref", family, 512)
    _require_non_empty_string(payload["canonical_score_ref"], "canonical_score_ref", family, 512)
    _require_non_empty_string(payload["threshold_decision_ref"], "threshold_decision_ref", family, 512)
    if not isinstance(payload["proposal_candidate_allowed"], bool):
        raise EvaluationSpineContractError(f"{family}.proposal_candidate_allowed must be boolean")
    if not isinstance(payload["rollback_required"], bool):
        raise EvaluationSpineContractError(f"{family}.rollback_required must be boolean")
    if "non_recalculation_notice" in payload and payload["non_recalculation_notice"] != FORGEMATH_NON_RECALCULATION_NOTICE:
        raise EvaluationSpineContractError(f"{family}.non_recalculation_notice is unsupported")


def _validate_forgehq_upstream_evidence_refs_shape(payload: Mapping[str, Any]) -> None:
    family = FORGEHQ_UPSTREAM_EVIDENCE_REFS_FAMILY
    required = {
        "schema_version",
        "forgehq_evidence_ref_id",
        "source_forge_eval_evidence_bundle_ref",
        "source_eval_calibration_report_ref",
        "source_forgemath_lane_evaluation_ref",
        "upstream_artifact_hashes",
        "non_authoritative_notice",
    }
    allowed = required | {"proposal_context_refs"}
    _require_keys(payload, required, family)
    _forbid_extra_keys(payload, allowed, family)

    if payload["schema_version"] != FORGEHQ_UPSTREAM_EVIDENCE_REFS_SCHEMA_VERSION:
        raise EvaluationSpineContractError(f"{family}.schema_version is unsupported")
    _require_non_empty_string(payload["forgehq_evidence_ref_id"], "forgehq_evidence_ref_id", family)
    _require_artifact_ref(payload["source_forge_eval_evidence_bundle_ref"], "source_forge_eval_evidence_bundle_ref", family)
    _require_artifact_ref(payload["source_eval_calibration_report_ref"], "source_eval_calibration_report_ref", family)
    _require_artifact_ref(payload["source_forgemath_lane_evaluation_ref"], "source_forgemath_lane_evaluation_ref", family)
    if payload["non_authoritative_notice"] != FORGEHQ_NON_AUTHORITATIVE_NOTICE:
        raise EvaluationSpineContractError(f"{family}.non_authoritative_notice is unsupported")

    hashes = payload["upstream_artifact_hashes"]
    if not isinstance(hashes, list) or not 1 <= len(hashes) <= 20:
        raise EvaluationSpineContractError(f"{family}.upstream_artifact_hashes must contain 1..20 entries")
    for index, item in enumerate(hashes):
        if not isinstance(item, Mapping):
            raise EvaluationSpineContractError(f"{family}.upstream_artifact_hashes[{index}] must be a mapping")
        _require_keys(item, {"artifact_family", "artifact_ref", "artifact_hash"}, family)
        _forbid_extra_keys(item, {"artifact_family", "artifact_ref", "artifact_hash"}, family)
        if item["artifact_family"] not in {
            "forge_eval_evidence_bundle",
            "eval_calibration_report",
            "forgemath_lane_evaluation_ref",
        }:
            raise EvaluationSpineContractError(f"{family}.upstream_artifact_hashes[{index}].artifact_family is unsupported")
        _require_artifact_ref(item["artifact_ref"], f"upstream_artifact_hashes[{index}].artifact_ref", family)
        _require_sha256(item["artifact_hash"], f"upstream_artifact_hashes[{index}].artifact_hash", family)

    if "proposal_context_refs" in payload:
        refs = payload["proposal_context_refs"]
        if not isinstance(refs, list) or len(refs) > 20 or any(not isinstance(ref, str) or len(ref) > 512 for ref in refs):
            raise EvaluationSpineContractError(f"{family}.proposal_context_refs must contain <= 20 strings <= 512 chars")
