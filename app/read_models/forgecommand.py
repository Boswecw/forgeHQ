"""
ForgeCommand read models for forgeHQ — Phase 6.

These types define the shapes exposed to the ForgeCommand review surface.
They are assembled from persisted backbone artifacts via the
ForgeCommandReadModelService.

Design principles:
- Evidence, rationale, challenge, and risk are presented in separate layers.
- Reviewability state is explicit and visible — never assumed.
- Approval actions are blocked when reviewability_state is NOT_REVIEWABLE.
- Proposal lifecycle state and operator decision state are always separate.
- All read models are non-authoritative — they present proposals, not facts.
"""
from dataclasses import dataclass, field

from app.domain.reviewability.enums import (
    ChallengePosture,
    NotReviewableReason,
    OperatorDecisionState,
    ProposalLifecycleState,
    ReviewabilityState,
    VerificationPosture,
)


@dataclass(frozen=True, slots=True)
class ProposalQueueItem:
    """One item in the ForgeCommand proposal review queue."""

    proposal_artifact_id: str
    run_id: str
    target_id: str
    change_hypothesis: str
    reviewability_state: ReviewabilityState
    proposal_lifecycle_state: ProposalLifecycleState
    operator_decision_state: OperatorDecisionState
    challenge_posture: ChallengePosture
    verification_posture: VerificationPosture
    # Human-readable summary for queue display.
    summary: str
    # Approval actions are only available when reviewability_state is REVIEWABLE.
    approval_actions_available: bool


@dataclass(frozen=True, slots=True)
class EvidenceLayer:
    """Deterministic evidence contributing to the proposal's target selection."""

    admitted_source_refs: tuple[str, ...]
    target_id: str
    composite_ranking_score: float
    ranking_factor_count: int


@dataclass(frozen=True, slots=True)
class RationaleLayer:
    """Design rationale for the candidate change."""

    change_hypothesis: str
    intended_confidence_gain: str
    targeted_behaviors: tuple[str, ...]
    oracle_strategy: str
    scope_boundary_statement: str
    modified_refs: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class ChallengeLayer:
    """Independent challenge findings from the Critic/Falsifier lane."""

    challenge_posture: ChallengePosture
    downgrade_applied: bool
    contradictions: tuple[str, ...]
    duplicate_test_warnings: tuple[str, ...]
    shallow_gain_indicators: tuple[str, ...]
    residual_concerns: tuple[str, ...]
    disconfirming_checks_evaluated: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class RiskLayer:
    """Residual risk and verification limitations."""

    verification_posture: VerificationPosture
    observed_gains: tuple[str, ...]
    residual_weaknesses: tuple[str, ...]
    measurement_basis: tuple[str, ...]
    failure_hypotheses: tuple[str, ...]
    disconfirming_checks: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class ProposalDetailModel:
    """
    Full layered detail view of a proposal for the ForgeCommand review surface.

    Layers are kept separate so the operator can interrogate each concern
    independently rather than being presented a collapsed summary.

    approval_blocked_reason is non-None when approval_actions_available is False,
    explaining why the proposal cannot be actioned.
    """

    proposal_artifact_id: str
    run_id: str
    reviewability_state: ReviewabilityState
    not_reviewable_reasons: tuple[NotReviewableReason, ...]
    proposal_lifecycle_state: ProposalLifecycleState
    operator_decision_state: OperatorDecisionState
    approval_actions_available: bool
    approval_blocked_reason: str | None

    # Layered review surfaces — each presented independently.
    evidence: EvidenceLayer
    rationale: RationaleLayer
    challenge: ChallengeLayer
    risk: RiskLayer

    overall_confidence_narrative: str
    non_authoritative_notice: str
