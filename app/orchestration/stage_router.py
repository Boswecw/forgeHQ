from types import MappingProxyType
from typing import Final, Mapping

from app.domain.artifacts.enums import ArtifactFamily
from app.domain.pipeline.enums import PIPELINE_STAGE_ORDER, PipelineStage
from app.schemas._base import ArtifactStub
from app.schemas.shaping_run import ShapingRun


class StageTransitionError(ValueError):
    """Base error for fail-closed stage transition violations."""


class InvalidStageTransitionError(StageTransitionError):
    """Raised when a shaping run attempts an invalid stage transition."""


class MissingRequiredArtifactError(StageTransitionError):
    """Raised when a stage is missing the artifacts required to begin."""


class InvalidStageEmissionError(StageTransitionError):
    """Raised when a stage emits the wrong artifact families."""


REQUIRED_PREDECESSOR_ARTIFACTS: Final[Mapping[PipelineStage, tuple[ArtifactFamily, ...]]] = (
    MappingProxyType(
        {
            PipelineStage.SIGNAL_INTAKE: (),
            PipelineStage.TARGET_RANKING: (ArtifactFamily.SIGNAL_SNAPSHOT,),
            PipelineStage.CONTEXT_CURATION: (
                ArtifactFamily.SIGNAL_SNAPSHOT,
                ArtifactFamily.TARGET_RANKING,
            ),
            PipelineStage.CANDIDATE_DESIGN: (ArtifactFamily.CONTEXT_BUNDLE,),
            PipelineStage.CANDIDATE_GENERATION: (ArtifactFamily.CANDIDATE_DESIGN,),
            PipelineStage.FALSIFICATION: (ArtifactFamily.CANDIDATE_PATCH,),
            PipelineStage.VERIFICATION: (ArtifactFamily.CANDIDATE_PATCH,),
            PipelineStage.PROPOSAL_PACKAGING: (
                ArtifactFamily.SIGNAL_SNAPSHOT,
                ArtifactFamily.TARGET_RANKING,
                ArtifactFamily.CONTEXT_BUNDLE,
                ArtifactFamily.CANDIDATE_DESIGN,
                ArtifactFamily.CANDIDATE_PATCH,
                ArtifactFamily.FALSIFICATION_REPORT,
                ArtifactFamily.CANDIDATE_VERIFICATION,
            ),
        }
    )
)


REQUIRED_STAGE_EMISSIONS: Final[Mapping[PipelineStage, tuple[ArtifactFamily, ...]]] = MappingProxyType(
    {
        PipelineStage.SIGNAL_INTAKE: (ArtifactFamily.SIGNAL_SNAPSHOT,),
        PipelineStage.TARGET_RANKING: (ArtifactFamily.TARGET_RANKING,),
        PipelineStage.CONTEXT_CURATION: (ArtifactFamily.CONTEXT_BUNDLE,),
        PipelineStage.CANDIDATE_DESIGN: (ArtifactFamily.CANDIDATE_DESIGN,),
        PipelineStage.CANDIDATE_GENERATION: (ArtifactFamily.CANDIDATE_PATCH,),
        PipelineStage.FALSIFICATION: (ArtifactFamily.FALSIFICATION_REPORT,),
        PipelineStage.VERIFICATION: (ArtifactFamily.CANDIDATE_VERIFICATION,),
        PipelineStage.PROPOSAL_PACKAGING: (
            ArtifactFamily.CONFIDENCE_SHAPING_SUMMARY,
            ArtifactFamily.FORGEHQ_PROPOSAL,
        ),
    }
)


def next_stage_for(run: ShapingRun) -> PipelineStage | None:
    _validate_run_state(run)
    if len(run.completed_stages) >= len(PIPELINE_STAGE_ORDER):
        return None
    return PIPELINE_STAGE_ORDER[len(run.completed_stages)]


def validate_transition(run: ShapingRun, target_stage: PipelineStage) -> None:
    _validate_run_state(run)

    expected_stage = next_stage_for(run)
    if expected_stage is None:
        raise InvalidStageTransitionError(
            "shaping run is already complete; no further stage transitions are allowed"
        )
    if target_stage != expected_stage:
        raise InvalidStageTransitionError(
            f"invalid transition to {target_stage.value}; expected {expected_stage.value}"
        )

    missing_artifacts = tuple(
        artifact_family
        for artifact_family in REQUIRED_PREDECESSOR_ARTIFACTS[target_stage]
        if not run.has_artifact(artifact_family)
    )
    if missing_artifacts:
        missing = ", ".join(artifact.value for artifact in missing_artifacts)
        raise MissingRequiredArtifactError(
            f"missing required predecessor artifacts for {target_stage.value}: {missing}"
        )


def apply_transition(
    run: ShapingRun,
    target_stage: PipelineStage,
    emitted_artifacts: tuple[ArtifactStub, ...],
) -> ShapingRun:
    validate_transition(run, target_stage)

    emitted_families = tuple(artifact.artifact_family for artifact in emitted_artifacts)
    expected_families = REQUIRED_STAGE_EMISSIONS[target_stage]
    if emitted_families != expected_families:
        expected = ", ".join(artifact.value for artifact in expected_families)
        actual = ", ".join(artifact.value for artifact in emitted_families)
        raise InvalidStageEmissionError(
            f"invalid emitted artifact families for {target_stage.value}: "
            f"expected [{expected}] but received [{actual}]"
        )

    return run.with_transition(target_stage, emitted_artifacts)


def _validate_run_state(run: ShapingRun) -> None:
    expected_prefix = PIPELINE_STAGE_ORDER[: len(run.completed_stages)]
    if run.completed_stages != expected_prefix:
        raise InvalidStageTransitionError(
            "shaping run has a non-prefix completed stage history and cannot progress safely"
        )

    if run.current_stage is None and run.completed_stages:
        raise InvalidStageTransitionError(
            "shaping run has completed stages but no current stage marker"
        )

    if run.current_stage is not None and (
        not run.completed_stages or run.current_stage != run.completed_stages[-1]
    ):
        raise InvalidStageTransitionError(
            "shaping run current stage does not match the completed stage history"
        )

    artifact_families = tuple(artifact.artifact_family for artifact in run.artifacts)
    if len(artifact_families) != len(set(artifact_families)):
        raise InvalidStageTransitionError(
            "shaping run contains duplicate artifact families and cannot progress safely"
        )
