"""ForgeHQ proposal bridge for evaluation-spine upstream evidence.

This service converts validated upstream evidence payloads into a single
ForgeHQ-owned evidence-reference bundle. The bundle may be attached to later
proposal candidates, but this service does not create proposals, approve
proposals, execute remediations, or recalculate upstream authority.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any
from uuid import uuid4

from app.contracts.evaluation_spine import (
    FORGEHQ_NON_AUTHORITATIVE_NOTICE,
    EvaluationSpineContractError,
    compute_payload_hash,
    validate_eval_calibration_report_payload,
    validate_forgehq_upstream_evidence_refs_payload,
    validate_forgemath_lane_evaluation_ref_payload,
)


class ForgeHQProposalBridgeError(ValueError):
    """Raised when upstream evidence is unsafe for ForgeHQ proposal shaping."""


def build_forgehq_upstream_evidence_refs(
    *,
    eval_calibration_report: Mapping[str, Any],
    forgemath_lane_evaluation_ref: Mapping[str, Any],
    source_forgemath_lane_evaluation_ref: str,
    forgehq_evidence_ref_id: str | None = None,
    proposal_context_refs: Sequence[str] | None = None,
) -> dict[str, Any]:
    """Build a ForgeHQ upstream evidence-reference bundle.

    The bridge accepts only already-validated upstream evidence. It binds the
    Forge Eval -> Eval Calibration -> ForgeMath chain by comparing canonical
    payload hashes before emitting the ForgeHQ-owned reference bundle.
    """

    assert_forgehq_proposal_bridge_inputs(
        eval_calibration_report=eval_calibration_report,
        forgemath_lane_evaluation_ref=forgemath_lane_evaluation_ref,
    )

    source_forge_eval_evidence_bundle_ref = str(
        eval_calibration_report["source_forge_eval_evidence_bundle_ref"]
    )
    source_eval_calibration_report_ref = str(
        forgemath_lane_evaluation_ref["source_eval_calibration_report_ref"]
    )

    eval_calibration_report_hash = compute_payload_hash(eval_calibration_report)
    forgemath_lane_evaluation_ref_hash = compute_payload_hash(forgemath_lane_evaluation_ref)

    payload: dict[str, Any] = {
        "schema_version": "forgehq.upstream_evidence_refs.v1",
        "forgehq_evidence_ref_id": forgehq_evidence_ref_id
        or f"forgehq_upstream_evidence_refs:{uuid4()}:v1",
        "source_forge_eval_evidence_bundle_ref": source_forge_eval_evidence_bundle_ref,
        "source_eval_calibration_report_ref": source_eval_calibration_report_ref,
        "source_forgemath_lane_evaluation_ref": source_forgemath_lane_evaluation_ref,
        "upstream_artifact_hashes": [
            {
                "artifact_family": "forge_eval_evidence_bundle",
                "artifact_ref": source_forge_eval_evidence_bundle_ref,
                "artifact_hash": str(eval_calibration_report["source_artifact_hash"]),
            },
            {
                "artifact_family": "eval_calibration_report",
                "artifact_ref": source_eval_calibration_report_ref,
                "artifact_hash": eval_calibration_report_hash,
            },
            {
                "artifact_family": "forgemath_lane_evaluation_ref",
                "artifact_ref": source_forgemath_lane_evaluation_ref,
                "artifact_hash": forgemath_lane_evaluation_ref_hash,
            },
        ],
        "non_authoritative_notice": FORGEHQ_NON_AUTHORITATIVE_NOTICE,
    }

    if proposal_context_refs is not None:
        payload["proposal_context_refs"] = list(proposal_context_refs)

    try:
        validate_forgehq_upstream_evidence_refs_payload(payload)
    except EvaluationSpineContractError as exc:
        raise ForgeHQProposalBridgeError(f"invalid ForgeHQ upstream evidence refs payload: {exc}") from exc
    return payload


def assert_forgehq_proposal_bridge_inputs(
    *,
    eval_calibration_report: Mapping[str, Any],
    forgemath_lane_evaluation_ref: Mapping[str, Any],
) -> None:
    """Fail closed unless upstream evidence is safe to reference."""

    try:
        validate_eval_calibration_report_payload(eval_calibration_report)
        validate_forgemath_lane_evaluation_ref_payload(forgemath_lane_evaluation_ref)
    except EvaluationSpineContractError as exc:
        raise ForgeHQProposalBridgeError(f"invalid upstream evaluation-spine payload: {exc}") from exc

    if eval_calibration_report["validation_state"] != "passed":
        raise ForgeHQProposalBridgeError("eval calibration report did not pass validation")

    if forgemath_lane_evaluation_ref["proposal_candidate_allowed"] is not True:
        raise ForgeHQProposalBridgeError("ForgeMath did not allow proposal candidate shaping")

    if forgemath_lane_evaluation_ref["rollback_required"] is not False:
        raise ForgeHQProposalBridgeError("ForgeMath marked rollback as required")

    expected_eval_calibration_report_hash = compute_payload_hash(eval_calibration_report)
    observed_eval_calibration_report_hash = forgemath_lane_evaluation_ref["source_artifact_hash"]
    if observed_eval_calibration_report_hash != expected_eval_calibration_report_hash:
        raise ForgeHQProposalBridgeError(
            "ForgeMath source_artifact_hash does not match the supplied Eval Calibration report"
        )
