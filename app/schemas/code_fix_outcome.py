"""Code-fix outcome contract — the ground-truth learning signal (forgeHQ side).

CodeFixOutcome.v1 is what teaches NeuroForge's (model, category) champion which
model actually produced a verified, accepted, regression-free fix. Per the plan,
the layered evidence is preserved (NOT collapsed) and the scalar reward is DERIVED
from it — so the routing utility can be recomputed/re-weighted later.

This is the forgeHQ-side artifact; emitting it to NeuroForge's model-outcome
endpoint is the cloud step (A4, confirm-before-deploy). The endpoint joins it to the
generation via context_bundle_id + model_id.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum


class OutcomeStage(StrEnum):
    VERIFIED = "verified"      # tier-1 deterministic (pact-verify)
    ACCEPTED = "accepted"      # tier-4 operator accept
    APPLIED = "applied"        # applied; tier-2 CI/checks
    REJECTED = "rejected"      # tier-4 operator reject
    REGRESSED = "regressed"    # tier-3 post-apply regression


@dataclass(frozen=True, slots=True)
class EvidenceItem:
    """One independent evidence signal, kept un-collapsed."""

    tier: int          # 1=deterministic … 7=self-eval (plan evidence hierarchy)
    name: str          # pact_verify | ci_green | operator_accept | no_regression | ...
    passed: bool
    detail: str = ""


@dataclass(frozen=True, slots=True)
class CodeFixOutcome:
    """Ground-truth outcome for one (model, category) generation."""

    # join + identity
    context_bundle_id: str
    task_intent_id: str | None
    model_id: str | None
    tier: str | None

    # the "what"
    routing_cell: str
    family: str
    kind: str
    language: str
    complexity: str
    risk: str

    # the signal
    stage: str
    evidence: tuple[EvidenceItem, ...]
    reward: float                      # DERIVED from evidence (see derive_reward)

    source_system: str = "forgehq"
    classification_method: str = ""
    evidence_summary: dict[str, bool] = field(default_factory=dict)
