"""Build CodeFixOutcome from a classification + generation identity + staged evidence.

Evidence accrues across stages (verify → operator accept → applied/CI → regression);
the scalar reward is DERIVED from the accumulated layered evidence each time, never
stored as the only truth. This is the forgeHQ-side producer of the learning signal;
the NeuroForge model-outcome endpoint (A4) consumes it to update the (model, category)
champion EMA.
"""
from __future__ import annotations

from app.drivers.neuroforge_generator import GenerationResult
from app.schemas.code_fix_classification import CodeFixClassification
from app.schemas.code_fix_outcome import CodeFixOutcome, EvidenceItem, OutcomeStage


def derive_reward(evidence: tuple[EvidenceItem, ...]) -> float:
    """Derive the 0..1 reward from the un-collapsed evidence (operative tiers today).

    Hard zeros first (failed deterministic / regression), then build up:
    verify-pass 0.6 → +operator-accept 0.8 → +clean-apply (CI) 1.0; reject 0.1.
    """
    by_name = {e.name: e for e in evidence}

    if "pact_verify" in by_name and not by_name["pact_verify"].passed:
        return 0.0
    if "no_regression" in by_name and not by_name["no_regression"].passed:
        return 0.0
    if "operator_accept" in by_name and not by_name["operator_accept"].passed:
        return 0.1

    reward = 0.0
    if by_name.get("pact_verify") and by_name["pact_verify"].passed:
        reward = 0.6
    if by_name.get("operator_accept") and by_name["operator_accept"].passed:
        reward = 0.8
    if by_name.get("ci_green") and by_name["ci_green"].passed:
        reward = 1.0
    return reward


class CodeFixOutcomeBuilder:
    """Accumulates evidence for one generation and emits CodeFixOutcome per stage."""

    def __init__(
        self,
        *,
        classification: CodeFixClassification,
        generation: GenerationResult,
        context_bundle_id: str,
        task_intent_id: str | None = None,
    ) -> None:
        self._c = classification
        self._gen = generation
        self._context_bundle_id = context_bundle_id
        self._task_intent_id = task_intent_id
        self._evidence: list[EvidenceItem] = []

    def _emit(self, stage: OutcomeStage) -> CodeFixOutcome:
        evidence = tuple(self._evidence)
        return CodeFixOutcome(
            context_bundle_id=self._context_bundle_id,
            task_intent_id=self._task_intent_id,
            model_id=self._gen.model_id,
            tier=self._gen.tier,
            routing_cell=self._c.routing_cell,
            family=self._c.family,
            kind=self._c.kind,
            language=self._c.language,
            complexity=self._c.complexity,
            risk=self._c.risk,
            stage=stage.value,
            evidence=evidence,
            reward=derive_reward(evidence),
            classification_method=self._c.classification_method,
            evidence_summary={e.name: e.passed for e in evidence},
        )

    def verified(self, ok: bool, detail: str = "") -> CodeFixOutcome:
        self._evidence.append(EvidenceItem(tier=1, name="pact_verify", passed=ok, detail=detail))
        return self._emit(OutcomeStage.VERIFIED)

    def accepted(self) -> CodeFixOutcome:
        self._evidence.append(EvidenceItem(tier=4, name="operator_accept", passed=True))
        return self._emit(OutcomeStage.ACCEPTED)

    def rejected(self, reason: str = "") -> CodeFixOutcome:
        self._evidence.append(EvidenceItem(tier=4, name="operator_accept", passed=False, detail=reason))
        return self._emit(OutcomeStage.REJECTED)

    def applied(self, ci_green: bool, detail: str = "") -> CodeFixOutcome:
        self._evidence.append(EvidenceItem(tier=2, name="ci_green", passed=ci_green, detail=detail))
        return self._emit(OutcomeStage.APPLIED)

    def regressed(self, detail: str = "") -> CodeFixOutcome:
        self._evidence.append(EvidenceItem(tier=3, name="no_regression", passed=False, detail=detail))
        return self._emit(OutcomeStage.REGRESSED)
