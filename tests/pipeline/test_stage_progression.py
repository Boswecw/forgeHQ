import pytest

from app.domain.artifacts.enums import ArtifactFamily
from app.domain.pipeline.enums import PIPELINE_STAGE_ORDER, PipelineStage
from app.domain.reviewability.enums import ProposalLifecycleState
from app.orchestration.forgehq_orchestrator import ForgeHQOrchestrator
from app.orchestration.stage_router import InvalidStageTransitionError


def test_valid_noop_progression_through_all_stages():
    orchestrator = ForgeHQOrchestrator()

    run = orchestrator.run_noop_pipeline(run_id="noop-run")

    assert run.completed_stages == PIPELINE_STAGE_ORDER
    assert run.current_stage == PipelineStage.PROPOSAL_PACKAGING
    assert run.proposal_lifecycle_state == ProposalLifecycleState.PACKAGED
    assert run.has_artifact(ArtifactFamily.SIGNAL_SNAPSHOT)
    assert run.has_artifact(ArtifactFamily.TARGET_RANKING)
    assert run.has_artifact(ArtifactFamily.CONTEXT_BUNDLE)
    assert run.has_artifact(ArtifactFamily.CANDIDATE_DESIGN)
    assert run.has_artifact(ArtifactFamily.CANDIDATE_PATCH)
    assert run.has_artifact(ArtifactFamily.FALSIFICATION_REPORT)
    assert run.has_artifact(ArtifactFamily.CANDIDATE_VERIFICATION)
    assert run.has_artifact(ArtifactFamily.CONFIDENCE_SHAPING_SUMMARY)
    assert run.has_artifact(ArtifactFamily.FORGEHQ_PROPOSAL)


def test_invalid_stage_skip_rejection():
    orchestrator = ForgeHQOrchestrator()
    run = orchestrator.start_run(run_id="skip-run")
    run = orchestrator.advance_to_stage(run, PipelineStage.SIGNAL_INTAKE)

    with pytest.raises(InvalidStageTransitionError, match="expected target_ranking"):
        orchestrator.advance_to_stage(run, PipelineStage.CONTEXT_CURATION)
