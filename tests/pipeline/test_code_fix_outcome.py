"""Tests for generation-metadata capture + layered outcome building + reward derivation."""
from app.drivers.neuroforge_generator import GenerationResult
from app.schemas.code_fix_classification import (
    CodeFixClassification,
    RiskFloorResolution,
)
from app.schemas.code_fix_outcome import EvidenceItem
from app.services.code_fix_outcome_builder import CodeFixOutcomeBuilder, derive_reward


def _classification(kind="bugfix_logic", risk="standard"):
    return CodeFixClassification(
        family="code_fix",
        kind=kind,
        secondary_kinds=(),
        language="python",
        complexity="local",
        routing_cell=f"code_fix:{kind}:python:local",
        risk=risk,
        min_tier=None,
        risk_resolution=RiskFloorResolution(
            explicit_risk=risk, primary_kind=kind, primary_kind_floor=risk,
            secondary_kind_floors=(), effective_risk=risk, min_tier=None, rationale="t",
        ),
    )


def _gen(model_id="deepseek-chat", tier="STANDARD"):
    return GenerationResult(content="def x(): return 1\n", model_id=model_id, tier=tier, raw={})


def _builder():
    return CodeFixOutcomeBuilder(
        classification=_classification(),
        generation=_gen(),
        context_bundle_id="ctxb_abc",
        task_intent_id="ti_codefix_1",
    )


# --- reward derivation from layered evidence (operative tiers) ---

def test_reward_ladder():
    assert derive_reward((EvidenceItem(1, "pact_verify", False),)) == 0.0
    assert derive_reward((EvidenceItem(1, "pact_verify", True),)) == 0.6
    assert derive_reward((EvidenceItem(1, "pact_verify", True), EvidenceItem(4, "operator_accept", True))) == 0.8
    assert derive_reward((
        EvidenceItem(1, "pact_verify", True),
        EvidenceItem(4, "operator_accept", True),
        EvidenceItem(2, "ci_green", True),
    )) == 1.0


def test_reward_reject_and_regression_are_low():
    assert derive_reward((EvidenceItem(1, "pact_verify", True), EvidenceItem(4, "operator_accept", False))) == 0.1
    assert derive_reward((
        EvidenceItem(1, "pact_verify", True),
        EvidenceItem(4, "operator_accept", True),
        EvidenceItem(2, "ci_green", True),
        EvidenceItem(3, "no_regression", False),
    )) == 0.0


# --- builder accrues evidence across stages, carries identity + the 'what' ---

def test_builder_verified_carries_identity_and_evidence():
    o = _builder().verified(True)
    assert o.stage == "verified"
    assert o.context_bundle_id == "ctxb_abc"
    assert o.model_id == "deepseek-chat"
    assert o.tier == "STANDARD"
    assert o.routing_cell == "code_fix:bugfix_logic:python:local"
    assert o.reward == 0.6
    assert o.evidence_summary == {"pact_verify": True}


def test_builder_accrues_to_full_reward():
    b = _builder()
    assert b.verified(True).reward == 0.6
    assert b.accepted().reward == 0.8
    applied = b.applied(ci_green=True)
    assert applied.reward == 1.0
    assert applied.stage == "applied"
    # evidence preserved un-collapsed across all three stages
    assert {e.name for e in applied.evidence} == {"pact_verify", "operator_accept", "ci_green"}


def test_builder_verify_fail_blocks_reward():
    o = _builder().verified(False, detail="grounding mismatch")
    assert o.reward == 0.0
    assert o.stage == "verified"


def test_builder_rejected_path():
    b = _builder()
    b.verified(True)
    o = b.rejected("operator declined")
    assert o.stage == "rejected"
    assert o.reward == 0.1
