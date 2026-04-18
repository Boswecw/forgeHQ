from dataclasses import dataclass, field

from app.domain.artifacts.enums import ArtifactFamily
from app.domain.pipeline.enums import PipelineStage
from app.schemas._base import ArtifactStub


@dataclass(frozen=True, slots=True)
class TargetRanking(ArtifactStub):
    """
    Non-authoritative ranking for a single bounded improvement target.

    composite_score: weighted aggregate of ranking factors (0.0–1.0).
    ranking_trace_artifact_id: artifact_id of the companion RankingFactorTrace
      that records per-factor explainability.

    Phase 1 placeholder uses default values for all fields.
    """

    artifact_family: ArtifactFamily = field(
        init=False,
        default=ArtifactFamily.TARGET_RANKING,
    )
    stage: PipelineStage = field(
        init=False,
        default=PipelineStage.TARGET_RANKING,
    )
    ranked_target_id: str = "placeholder-target"
    composite_score: float = 0.0
    ranking_trace_artifact_id: str | None = None
    summary: str = "Placeholder ranking for a single bounded improvement target."
