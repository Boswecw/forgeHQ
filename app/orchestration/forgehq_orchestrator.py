from dataclasses import dataclass
from typing import Final

from app.domain.artifacts.enums import ArtifactFamily
from app.domain.pipeline.enums import PIPELINE_STAGE_ORDER, PipelineStage, STAGE_OWNER
from app.domain.workers.enums import WorkerName
from app.orchestration.stage_router import REQUIRED_STAGE_EMISSIONS, apply_transition, validate_transition
from app.schemas._base import ArtifactStub
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


@dataclass(frozen=True, slots=True)
class WorkerInterfaceContract:
    stage: PipelineStage
    owner: WorkerName
    emitted_artifact_families: tuple[ArtifactFamily, ...]


WORKER_INTERFACE_CONTRACTS: Final[tuple[WorkerInterfaceContract, ...]] = tuple(
    WorkerInterfaceContract(
        stage=stage,
        owner=STAGE_OWNER[stage],
        emitted_artifact_families=REQUIRED_STAGE_EMISSIONS[stage],
    )
    for stage in PIPELINE_STAGE_ORDER
)


class ForgeHQOrchestrator:
    """Phase 1 no-op orchestrator that only advances bounded placeholder stages."""

    def start_run(self, run_id: str) -> ShapingRun:
        return ShapingRun(run_id=run_id)

    def advance_to_stage(self, run: ShapingRun, target_stage: PipelineStage) -> ShapingRun:
        validate_transition(run, target_stage)
        emitted_artifacts = self._build_placeholder_artifacts(run, target_stage)
        return apply_transition(run, target_stage, emitted_artifacts)

    def run_noop_pipeline(self, run_id: str) -> ShapingRun:
        run = self.start_run(run_id)
        for stage in PIPELINE_STAGE_ORDER:
            run = self.advance_to_stage(run, stage)
        return run

    def _build_placeholder_artifacts(
        self,
        run: ShapingRun,
        target_stage: PipelineStage,
    ) -> tuple[ArtifactStub, ...]:
        if target_stage == PipelineStage.SIGNAL_INTAKE:
            return (SignalSnapshot(run_id=run.run_id),)

        if target_stage == PipelineStage.TARGET_RANKING:
            signal_snapshot = run.get_artifact(ArtifactFamily.SIGNAL_SNAPSHOT)
            return (
                TargetRanking(
                    run_id=run.run_id,
                    parent_artifact_ids=(signal_snapshot.artifact_id,),
                ),
            )

        if target_stage == PipelineStage.CONTEXT_CURATION:
            ranking = run.get_artifact(ArtifactFamily.TARGET_RANKING)
            return (
                ContextBundle(
                    run_id=run.run_id,
                    parent_artifact_ids=(ranking.artifact_id,),
                ),
            )

        if target_stage == PipelineStage.CANDIDATE_DESIGN:
            context_bundle = run.get_artifact(ArtifactFamily.CONTEXT_BUNDLE)
            return (
                CandidateDesign(
                    run_id=run.run_id,
                    parent_artifact_ids=(context_bundle.artifact_id,),
                ),
            )

        if target_stage == PipelineStage.CANDIDATE_GENERATION:
            design = run.get_artifact(ArtifactFamily.CANDIDATE_DESIGN)
            return (
                CandidatePatch(
                    run_id=run.run_id,
                    design_artifact_id=design.artifact_id,
                    parent_artifact_ids=(design.artifact_id,),
                ),
            )

        if target_stage == PipelineStage.FALSIFICATION:
            candidate_patch = run.get_artifact(ArtifactFamily.CANDIDATE_PATCH)
            return (
                FalsificationReport(
                    run_id=run.run_id,
                    challenged_patch_artifact_id=candidate_patch.artifact_id,
                    parent_artifact_ids=(candidate_patch.artifact_id,),
                ),
            )

        if target_stage == PipelineStage.VERIFICATION:
            candidate_patch = run.get_artifact(ArtifactFamily.CANDIDATE_PATCH)
            return (
                CandidateVerification(
                    run_id=run.run_id,
                    verified_patch_artifact_id=candidate_patch.artifact_id,
                    parent_artifact_ids=(candidate_patch.artifact_id,),
                ),
            )

        if target_stage == PipelineStage.PROPOSAL_PACKAGING:
            falsification = run.get_artifact(ArtifactFamily.FALSIFICATION_REPORT)
            verification = run.get_artifact(ArtifactFamily.CANDIDATE_VERIFICATION)
            confidence_summary = ConfidenceShapingSummary(
                run_id=run.run_id,
                falsification_artifact_id=falsification.artifact_id,
                verification_artifact_id=verification.artifact_id,
                parent_artifact_ids=(falsification.artifact_id, verification.artifact_id),
            )
            proposal = ForgeHQProposal(
                run_id=run.run_id,
                confidence_summary_artifact_id=confidence_summary.artifact_id,
                parent_artifact_ids=(confidence_summary.artifact_id,),
            )
            return (confidence_summary, proposal)

        raise ValueError(f"unsupported stage for Phase 1 placeholder orchestration: {target_stage}")
