from app.domain.artifacts.enums import (
    ARTIFACT_FAMILY_REGISTRY,
    ArtifactFamily,
    REQUIRED_REVIEWABILITY_BACKBONE,
    enum_values,
)
from app.domain.pipeline.enums import PIPELINE_STAGE_ORDER, PipelineStage
from app.domain.reviewability.enums import (
    AllowedLanguageToken,
    NotReviewableReason,
    OperatorDecisionState,
    ProposalLifecycleState,
    ProhibitedLanguageToken,
    ReviewabilityRequirement,
    contains_non_authoritative_language,
    contains_prohibited_authoritative_language,
)


def test_artifact_family_enum_and_registry_are_complete():
    expected_families = {
        "signal_snapshot",
        "intake_diagnostics",
        "target_ranking",
        "ranking_factor_trace",
        "context_bundle",
        "candidate_design",
        "candidate_patch",
        "falsification_report",
        "candidate_verification",
        "confidence_shaping_summary",
        "forgehq_proposal",
        "forgehq_evidence_bundle",
    }

    assert set(enum_values(ArtifactFamily)) == expected_families
    assert set(ARTIFACT_FAMILY_REGISTRY) == set(ArtifactFamily)
    assert set(REQUIRED_REVIEWABILITY_BACKBONE) == {
        ArtifactFamily.SIGNAL_SNAPSHOT,
        ArtifactFamily.TARGET_RANKING,
        ArtifactFamily.CONTEXT_BUNDLE,
        ArtifactFamily.CANDIDATE_DESIGN,
        ArtifactFamily.CANDIDATE_PATCH,
        ArtifactFamily.FALSIFICATION_REPORT,
        ArtifactFamily.CANDIDATE_VERIFICATION,
        ArtifactFamily.CONFIDENCE_SHAPING_SUMMARY,
        ArtifactFamily.FORGEHQ_PROPOSAL,
    }


def test_pipeline_stage_order_is_complete_and_fixed():
    assert PIPELINE_STAGE_ORDER == (
        PipelineStage.SIGNAL_INTAKE,
        PipelineStage.TARGET_RANKING,
        PipelineStage.CONTEXT_CURATION,
        PipelineStage.CANDIDATE_DESIGN,
        PipelineStage.CANDIDATE_GENERATION,
        PipelineStage.FALSIFICATION,
        PipelineStage.VERIFICATION,
        PipelineStage.PROPOSAL_PACKAGING,
    )


def test_reviewability_requires_challenge_and_verification():
    assert ReviewabilityRequirement.CHALLENGE_PRESENT.value == "challenge present"
    assert ReviewabilityRequirement.VERIFICATION_PRESENT.value == "verification present"
    assert NotReviewableReason.MISSING_CHALLENGE_ARTIFACT.value == "missing challenge artifact"
    assert NotReviewableReason.MISSING_VERIFICATION_ARTIFACT.value == "missing verification artifact"


def test_non_authoritative_language_policy_is_disjoint_and_enforced():
    allowed_values = {token.value for token in AllowedLanguageToken}
    prohibited_values = {token.value for token in ProhibitedLanguageToken}

    assert allowed_values.isdisjoint(prohibited_values)
    assert contains_non_authoritative_language(
        "This candidate suggests a bounded change and records residual concern."
    )
    assert contains_prohibited_authoritative_language(
        "This proposal is approved and must apply immediately."
    )


def test_proposal_lifecycle_state_never_collapses_into_operator_decision_state():
    lifecycle_values = {state.value for state in ProposalLifecycleState}
    operator_values = {state.value for state in OperatorDecisionState}

    assert lifecycle_values.isdisjoint(operator_values)
    assert "approved" not in lifecycle_values
    assert "accepted_by_operator" not in lifecycle_values
