from dataclasses import dataclass, field

from app.domain.artifacts.enums import ArtifactFamily
from app.domain.pipeline.enums import PipelineStage
from app.schemas._base import ArtifactStub


@dataclass(frozen=True, slots=True)
class CandidateDesign(ArtifactStub):
    artifact_family: ArtifactFamily = field(
        init=False,
        default=ArtifactFamily.CANDIDATE_DESIGN,
    )
    stage: PipelineStage = field(
        init=False,
        default=PipelineStage.CANDIDATE_DESIGN,
    )
    intended_confidence_gain: str = "placeholder-confidence-gain"
    oracle_strategy: str = "placeholder-oracle-strategy"
    summary: str = "Placeholder candidate design that exists before generation."
