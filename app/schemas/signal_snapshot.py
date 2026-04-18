from dataclasses import dataclass, field

from app.domain.artifacts.enums import ArtifactFamily
from app.domain.pipeline.enums import PipelineStage
from app.schemas._base import ArtifactStub


@dataclass(frozen=True, slots=True)
class SignalSnapshot(ArtifactStub):
    """
    Admitted signal snapshot produced by SignalIntakeService.

    source_refs: all refs that passed admissibility (i.e. admitted_source_refs).
    admitted_source_refs: explicit admitted subset (Phase 2+).
    rejected_source_refs: refs that failed admissibility (Phase 2+).

    Phase 1 placeholder uses default values for all fields.
    """

    artifact_family: ArtifactFamily = field(
        init=False,
        default=ArtifactFamily.SIGNAL_SNAPSHOT,
    )
    stage: PipelineStage = field(
        init=False,
        default=PipelineStage.SIGNAL_INTAKE,
    )
    source_refs: tuple[str, ...] = ("placeholder://signal-snapshot",)
    admitted_source_refs: tuple[str, ...] = ()
    rejected_source_refs: tuple[str, ...] = ()
    summary: str = "Placeholder admitted signal snapshot."
