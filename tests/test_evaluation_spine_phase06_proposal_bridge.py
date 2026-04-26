from __future__ import annotations

import re
from pathlib import Path

import pytest

from app.contracts.evaluation_spine import compute_payload_hash
from app.services.evaluation_spine_proposal_bridge import (
    ForgeHQProposalBridgeError,
    build_forgehq_upstream_evidence_refs,
)


FORGE_EVAL_REF = "forge_eval_evidence_bundle:00000000-0000-4000-8000-000000000001:v1"
EVAL_CAL_REF = "eval_calibration_report:00000000-0000-4000-8000-000000000002:v1"
FORGEMATH_REF = "forgemath_lane_evaluation_ref:00000000-0000-4000-8000-000000000003:v1"
FAKE_FORGE_EVAL_HASH = "sha256:" + "a" * 64


def _valid_eval_calibration_report() -> dict:
    return {
        "schema_version": "eval_cal_node.calibration_report.v1",
        "calibration_report_id": "calibration-report-0001",
        "source_forge_eval_evidence_bundle_ref": FORGE_EVAL_REF,
        "source_artifact_hash": FAKE_FORGE_EVAL_HASH,
        "repository_id": "ForgeHQ",
        "score_normalization_version": "self-healing-candidate-confidence-v1",
        "calibrated_scores": [
            {
                "metric_name": "candidate_confidence",
                "raw_score": 0.91,
                "calibrated_score": 0.87,
                "weight": 1.0,
            }
        ],
        "confidence_band_candidate": "high_confidence",
        "threshold_crossings": [
            {
                "threshold_id": "proposal_candidate_minimum",
                "crossed": True,
                "direction": "above",
            }
        ],
        "validation_state": "passed",
    }


def _valid_forgemath_lane_ref(eval_report: dict) -> dict:
    return {
        "schema_version": "forgemath.lane_evaluation_ref.v1",
        "lane_id": "self_healing_candidate_confidence_v1",
        "lane_version": 1,
        "source_eval_calibration_report_ref": EVAL_CAL_REF,
        "source_artifact_hash": compute_payload_hash(eval_report),
        "canonical_evaluation_ref": "forgemath://canonical/evaluations/self-healing-candidate-confidence-v1/0001",
        "canonical_score_ref": "forgemath://canonical/scores/self-healing-candidate-confidence-v1/0001",
        "threshold_decision_ref": "forgemath://canonical/threshold-decisions/self-healing-candidate-confidence-v1/0001",
        "proposal_candidate_allowed": True,
        "rollback_required": False,
        "non_recalculation_notice": (
            "Downstream systems must reference this ForgeMath result and must not recalculate "
            "canonical confidence, band, threshold, proposal allowance, or rollback decision."
        ),
    }


def test_phase06_builds_forgehq_upstream_evidence_refs_without_becoming_authority() -> None:
    eval_report = _valid_eval_calibration_report()
    lane_ref = _valid_forgemath_lane_ref(eval_report)

    payload = build_forgehq_upstream_evidence_refs(
        eval_calibration_report=eval_report,
        forgemath_lane_evaluation_ref=lane_ref,
        source_forgemath_lane_evaluation_ref=FORGEMATH_REF,
        forgehq_evidence_ref_id="forgehq-upstream-evidence-0001",
        proposal_context_refs=["forgehq://proposal-context/self-healing/0001"],
    )

    assert payload["schema_version"] == "forgehq.upstream_evidence_refs.v1"
    assert payload["source_forge_eval_evidence_bundle_ref"] == FORGE_EVAL_REF
    assert payload["source_eval_calibration_report_ref"] == EVAL_CAL_REF
    assert payload["source_forgemath_lane_evaluation_ref"] == FORGEMATH_REF
    assert payload["non_authoritative_notice"].startswith("ForgeHQ may reference upstream evidence")
    assert "proposal_decision" not in payload
    assert "approved" not in payload

    hashes = {item["artifact_family"]: item for item in payload["upstream_artifact_hashes"]}
    assert set(hashes) == {
        "forge_eval_evidence_bundle",
        "eval_calibration_report",
        "forgemath_lane_evaluation_ref",
    }
    assert hashes["forge_eval_evidence_bundle"]["artifact_hash"] == FAKE_FORGE_EVAL_HASH
    assert hashes["eval_calibration_report"]["artifact_hash"] == compute_payload_hash(eval_report)
    assert hashes["forgemath_lane_evaluation_ref"]["artifact_hash"] == compute_payload_hash(lane_ref)


@pytest.mark.parametrize(
    ("field", "value", "expected_message"),
    [
        ("validation_state", "failed", "did not pass validation"),
        ("validation_state", "blocked", "did not pass validation"),
    ],
)
def test_phase06_rejects_eval_calibration_reports_that_are_not_passed(
    field: str,
    value: str,
    expected_message: str,
) -> None:
    eval_report = _valid_eval_calibration_report()
    eval_report[field] = value
    lane_ref = _valid_forgemath_lane_ref(eval_report)

    with pytest.raises(ForgeHQProposalBridgeError, match=expected_message):
        build_forgehq_upstream_evidence_refs(
            eval_calibration_report=eval_report,
            forgemath_lane_evaluation_ref=lane_ref,
            source_forgemath_lane_evaluation_ref=FORGEMATH_REF,
        )


def test_phase06_rejects_when_forgemath_disallows_proposal_candidate() -> None:
    eval_report = _valid_eval_calibration_report()
    lane_ref = _valid_forgemath_lane_ref(eval_report)
    lane_ref["proposal_candidate_allowed"] = False

    with pytest.raises(ForgeHQProposalBridgeError, match="did not allow proposal candidate"):
        build_forgehq_upstream_evidence_refs(
            eval_calibration_report=eval_report,
            forgemath_lane_evaluation_ref=lane_ref,
            source_forgemath_lane_evaluation_ref=FORGEMATH_REF,
        )


def test_phase06_rejects_when_forgemath_requires_rollback() -> None:
    eval_report = _valid_eval_calibration_report()
    lane_ref = _valid_forgemath_lane_ref(eval_report)
    lane_ref["rollback_required"] = True

    with pytest.raises(ForgeHQProposalBridgeError, match="rollback as required"):
        build_forgehq_upstream_evidence_refs(
            eval_calibration_report=eval_report,
            forgemath_lane_evaluation_ref=lane_ref,
            source_forgemath_lane_evaluation_ref=FORGEMATH_REF,
        )


def test_phase06_rejects_tampered_eval_report_after_forgemath_hash_binding() -> None:
    eval_report = _valid_eval_calibration_report()
    lane_ref = _valid_forgemath_lane_ref(eval_report)
    eval_report["calibrated_scores"][0]["calibrated_score"] = 0.12

    with pytest.raises(ForgeHQProposalBridgeError, match="source_artifact_hash does not match"):
        build_forgehq_upstream_evidence_refs(
            eval_calibration_report=eval_report,
            forgemath_lane_evaluation_ref=lane_ref,
            source_forgemath_lane_evaluation_ref=FORGEMATH_REF,
        )


def test_phase06_rejects_invalid_forgemath_artifact_ref() -> None:
    eval_report = _valid_eval_calibration_report()
    lane_ref = _valid_forgemath_lane_ref(eval_report)

    with pytest.raises(ForgeHQProposalBridgeError):
        build_forgehq_upstream_evidence_refs(
            eval_calibration_report=eval_report,
            forgemath_lane_evaluation_ref=lane_ref,
            source_forgemath_lane_evaluation_ref="not-a-canonical-ref",
        )


def test_phase06_bridge_does_not_import_upstream_implementation_repos() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    checked_files = [
        repo_root / "app" / "contracts" / "evaluation_spine.py",
        repo_root / "app" / "services" / "evaluation_spine_proposal_bridge.py",
    ]
    direct_import = re.compile(r"^\s*(?:from|import)\s+(forge_eval|eval_cal_node|forgemath)\b", re.MULTILINE)

    for path in checked_files:
        assert path.exists(), f"missing expected bridge file: {path}"
        assert not direct_import.search(path.read_text()), f"direct upstream repo import found in {path}"
