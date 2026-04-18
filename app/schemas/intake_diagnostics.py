from dataclasses import dataclass, field

from app.domain.artifacts.enums import ArtifactFamily
from app.domain.pipeline.enums import PipelineStage
from app.domain.signals.enums import AdmissibilityDecision, SourceAuthorityClass
from app.schemas._base import ArtifactStub


@dataclass(frozen=True, slots=True)
class SourceAdmissibilityRecord:
    """One intake decision record for a single source ref."""

    source_ref: str
    authority_class: SourceAuthorityClass
    decision: AdmissibilityDecision
    rejection_reason: str | None = None


@dataclass(frozen=True, slots=True)
class IntakeDiagnostics(ArtifactStub):
    """
    Admissibility diagnostics produced by SignalIntakeService.

    Records which source refs were admitted, which were rejected, and why.
    Non-authoritative — does not claim upstream truth.
    """

    artifact_family: ArtifactFamily = field(
        init=False,
        default=ArtifactFamily.INTAKE_DIAGNOSTICS,
    )
    stage: PipelineStage = field(
        init=False,
        default=PipelineStage.SIGNAL_INTAKE,
    )
    records: tuple[SourceAdmissibilityRecord, ...] = ()
    admitted_count: int = 0
    rejected_count: int = 0
    summary: str = "Placeholder intake diagnostics."
