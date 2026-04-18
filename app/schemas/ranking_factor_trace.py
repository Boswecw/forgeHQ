from dataclasses import dataclass, field

from app.domain.artifacts.enums import ArtifactFamily
from app.domain.pipeline.enums import PipelineStage
from app.schemas._base import ArtifactStub


@dataclass(frozen=True, slots=True)
class RankingFactor:
    """
    One explainability factor contributing to a target's composite ranking score.

    is_deterministic=True means the factor comes from a deterministic upstream
    source (ForgeEval or ForgeMath) and receives elevated weight in composite scoring.
    """

    factor_name: str
    raw_value: float
    normalized_score: float  # 0.0–1.0 bounded
    source_ref: str
    is_deterministic: bool
    explanation: str


@dataclass(frozen=True, slots=True)
class RankingFactorTrace(ArtifactStub):
    """
    Explainability trace for a TargetRanking artifact.

    Preserves which factors contributed to the composite score and their
    individual weights so ranking decisions remain auditable.
    Non-authoritative — does not claim deterministic upstream truth.
    """

    artifact_family: ArtifactFamily = field(
        init=False,
        default=ArtifactFamily.RANKING_FACTOR_TRACE,
    )
    stage: PipelineStage = field(
        init=False,
        default=PipelineStage.TARGET_RANKING,
    )
    target_id: str = "placeholder-target"
    factors: tuple[RankingFactor, ...] = ()
    composite_score: float = 0.0
    summary: str = "Placeholder ranking factor trace."
