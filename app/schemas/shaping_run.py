from dataclasses import dataclass, replace

from app.domain.artifacts.enums import ArtifactFamily
from app.domain.pipeline.enums import PipelineStage
from app.domain.reviewability.enums import ProposalLifecycleState
from app.schemas._base import ArtifactStub


@dataclass(frozen=True, slots=True)
class ShapingRun:
    run_id: str
    current_stage: PipelineStage | None = None
    completed_stages: tuple[PipelineStage, ...] = ()
    artifacts: tuple[ArtifactStub, ...] = ()
    proposal_lifecycle_state: ProposalLifecycleState = ProposalLifecycleState.DRAFT

    def artifact_index(self) -> dict[ArtifactFamily, ArtifactStub]:
        return {artifact.artifact_family: artifact for artifact in self.artifacts}

    def has_artifact(self, artifact_family: ArtifactFamily) -> bool:
        return artifact_family in self.artifact_index()

    def get_artifact(self, artifact_family: ArtifactFamily) -> ArtifactStub:
        return self.artifact_index()[artifact_family]

    def with_transition(
        self,
        stage: PipelineStage,
        emitted_artifacts: tuple[ArtifactStub, ...],
    ) -> "ShapingRun":
        lifecycle_state = self.proposal_lifecycle_state
        if stage == PipelineStage.PROPOSAL_PACKAGING:
            lifecycle_state = ProposalLifecycleState.PACKAGED

        return replace(
            self,
            current_stage=stage,
            completed_stages=self.completed_stages + (stage,),
            artifacts=self.artifacts + emitted_artifacts,
            proposal_lifecycle_state=lifecycle_state,
        )
