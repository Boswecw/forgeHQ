from dataclasses import replace

import pytest

from app.domain.artifacts.enums import ArtifactFamily
from app.domain.pipeline.enums import PIPELINE_STAGE_ORDER, PipelineStage
from app.orchestration.forgehq_orchestrator import ForgeHQOrchestrator
from app.orchestration.stage_router import MissingRequiredArtifactError
from app.schemas.context_bundle import ContextBundle
from app.schemas.shaping_run import ShapingRun
from app.schemas.signal_snapshot import SignalSnapshot
from app.schemas.target_ranking import TargetRanking


def test_generation_before_design_rejection():
    orchestrator = ForgeHQOrchestrator()
    run = ShapingRun(
        run_id="generation-without-design",
        current_stage=PipelineStage.CANDIDATE_DESIGN,
        completed_stages=PIPELINE_STAGE_ORDER[:4],
        artifacts=(
            SignalSnapshot(run_id="generation-without-design"),
            TargetRanking(
                run_id="generation-without-design",
                parent_artifact_ids=("signal",),
            ),
            ContextBundle(
                run_id="generation-without-design",
                parent_artifact_ids=("ranking",),
            ),
        ),
    )

    assert run.has_artifact(ArtifactFamily.CONTEXT_BUNDLE)
    assert not run.has_artifact(ArtifactFamily.CANDIDATE_DESIGN)

    with pytest.raises(MissingRequiredArtifactError, match="candidate_design"):
        orchestrator.advance_to_stage(run, PipelineStage.CANDIDATE_GENERATION)
