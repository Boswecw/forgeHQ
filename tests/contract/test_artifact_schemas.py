from app.domain.artifacts.enums import ArtifactAuthorityPosture, ArtifactFamily
from app.domain.pipeline.enums import PipelineStage
from app.domain.reviewability.enums import ProposalLifecycleState, ReviewabilityState
from app.schemas.candidate_design import CandidateDesign
from app.schemas.candidate_patch import CandidatePatch
from app.schemas.candidate_verification import CandidateVerification
from app.schemas.confidence_shaping_summary import ConfidenceShapingSummary
from app.schemas.context_bundle import ContextBundle
from app.schemas.falsification_report import FalsificationReport
from app.schemas.forgehq_proposal import ForgeHQProposal
from app.schemas.shaping_run import ShapingRun
from app.schemas.signal_snapshot import SignalSnapshot
from app.schemas.target_ranking import TargetRanking


def test_artifact_schema_defaults_preserve_non_authoritative_posture():
    artifacts = (
        SignalSnapshot(run_id="schema-test"),
        TargetRanking(run_id="schema-test"),
        ContextBundle(run_id="schema-test"),
        CandidateDesign(run_id="schema-test"),
        CandidatePatch(run_id="schema-test"),
        FalsificationReport(run_id="schema-test"),
        CandidateVerification(run_id="schema-test"),
        ConfidenceShapingSummary(run_id="schema-test"),
        ForgeHQProposal(run_id="schema-test"),
    )

    expected_pairs = {
        ArtifactFamily.SIGNAL_SNAPSHOT: PipelineStage.SIGNAL_INTAKE,
        ArtifactFamily.TARGET_RANKING: PipelineStage.TARGET_RANKING,
        ArtifactFamily.CONTEXT_BUNDLE: PipelineStage.CONTEXT_CURATION,
        ArtifactFamily.CANDIDATE_DESIGN: PipelineStage.CANDIDATE_DESIGN,
        ArtifactFamily.CANDIDATE_PATCH: PipelineStage.CANDIDATE_GENERATION,
        ArtifactFamily.FALSIFICATION_REPORT: PipelineStage.FALSIFICATION,
        ArtifactFamily.CANDIDATE_VERIFICATION: PipelineStage.VERIFICATION,
        ArtifactFamily.CONFIDENCE_SHAPING_SUMMARY: PipelineStage.PROPOSAL_PACKAGING,
        ArtifactFamily.FORGEHQ_PROPOSAL: PipelineStage.PROPOSAL_PACKAGING,
    }

    for artifact in artifacts:
        assert artifact.authority_posture == ArtifactAuthorityPosture.NON_AUTHORITATIVE
        assert artifact.artifact_family in expected_pairs
        assert artifact.stage == expected_pairs[artifact.artifact_family]
        assert artifact.placeholder is True
        assert "Non-authoritative" in artifact.non_authoritative_notice


def test_shaping_run_defaults_keep_lifecycle_state_separate():
    shaping_run = ShapingRun(run_id="schema-test")
    proposal = ForgeHQProposal(run_id="schema-test")

    assert shaping_run.proposal_lifecycle_state == ProposalLifecycleState.DRAFT
    assert proposal.reviewability_state == ReviewabilityState.NOT_REVIEWABLE
