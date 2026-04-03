import pytest

from app.domain.pipeline.enums import PIPELINE_STAGE_ORDER, PipelineStage
from app.orchestration.forgehq_orchestrator import ForgeHQOrchestrator
from app.orchestration.stage_router import MissingRequiredArtifactError
from app.schemas.candidate_design import CandidateDesign
from app.schemas.candidate_patch import CandidatePatch
from app.schemas.candidate_verification import CandidateVerification
from app.schemas.context_bundle import ContextBundle
from app.schemas.falsification_report import FalsificationReport
from app.schemas.shaping_run import ShapingRun
from app.schemas.signal_snapshot import SignalSnapshot
from app.schemas.target_ranking import TargetRanking


def test_packaging_before_falsification_rejection():
    orchestrator = ForgeHQOrchestrator()
    run = ShapingRun(
        run_id="missing-falsification",
        current_stage=PipelineStage.VERIFICATION,
        completed_stages=PIPELINE_STAGE_ORDER[:7],
        artifacts=(
            SignalSnapshot(run_id="missing-falsification"),
            TargetRanking(run_id="missing-falsification", parent_artifact_ids=("signal",)),
            ContextBundle(run_id="missing-falsification", parent_artifact_ids=("ranking",)),
            CandidateDesign(run_id="missing-falsification", parent_artifact_ids=("context",)),
            CandidatePatch(
                run_id="missing-falsification",
                design_artifact_id="design",
                parent_artifact_ids=("design",),
            ),
            CandidateVerification(
                run_id="missing-falsification",
                verified_patch_artifact_id="patch",
                parent_artifact_ids=("patch",),
            ),
        ),
    )

    with pytest.raises(MissingRequiredArtifactError, match="falsification_report"):
        orchestrator.advance_to_stage(run, PipelineStage.PROPOSAL_PACKAGING)


def test_packaging_before_verification_rejection():
    orchestrator = ForgeHQOrchestrator()
    run = ShapingRun(
        run_id="missing-verification",
        current_stage=PipelineStage.VERIFICATION,
        completed_stages=PIPELINE_STAGE_ORDER[:7],
        artifacts=(
            SignalSnapshot(run_id="missing-verification"),
            TargetRanking(run_id="missing-verification", parent_artifact_ids=("signal",)),
            ContextBundle(run_id="missing-verification", parent_artifact_ids=("ranking",)),
            CandidateDesign(run_id="missing-verification", parent_artifact_ids=("context",)),
            CandidatePatch(
                run_id="missing-verification",
                design_artifact_id="design",
                parent_artifact_ids=("design",),
            ),
            FalsificationReport(
                run_id="missing-verification",
                challenged_patch_artifact_id="patch",
                parent_artifact_ids=("patch",),
            ),
        ),
    )

    with pytest.raises(MissingRequiredArtifactError, match="candidate_verification"):
        orchestrator.advance_to_stage(run, PipelineStage.PROPOSAL_PACKAGING)
