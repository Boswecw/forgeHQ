from enum import StrEnum
from types import MappingProxyType
from typing import Final, Mapping

from app.domain.artifacts.enums import ArtifactFamily
from app.domain.workers.enums import WorkerName


class PipelineStage(StrEnum):
    SIGNAL_INTAKE = "signal_intake"
    TARGET_RANKING = "target_ranking"
    CONTEXT_CURATION = "context_curation"
    CANDIDATE_DESIGN = "candidate_design"
    CANDIDATE_GENERATION = "candidate_generation"
    FALSIFICATION = "falsification"
    VERIFICATION = "verification"
    PROPOSAL_PACKAGING = "proposal_packaging"


PIPELINE_STAGE_ORDER: Final[tuple[PipelineStage, ...]] = (
    PipelineStage.SIGNAL_INTAKE,
    PipelineStage.TARGET_RANKING,
    PipelineStage.CONTEXT_CURATION,
    PipelineStage.CANDIDATE_DESIGN,
    PipelineStage.CANDIDATE_GENERATION,
    PipelineStage.FALSIFICATION,
    PipelineStage.VERIFICATION,
    PipelineStage.PROPOSAL_PACKAGING,
)


STAGE_PRIMARY_ARTIFACTS: Final[Mapping[PipelineStage, tuple[ArtifactFamily, ...]]] = MappingProxyType(
    {
        PipelineStage.SIGNAL_INTAKE: (
            ArtifactFamily.SIGNAL_SNAPSHOT,
            ArtifactFamily.INTAKE_DIAGNOSTICS,
        ),
        PipelineStage.TARGET_RANKING: (
            ArtifactFamily.TARGET_RANKING,
            ArtifactFamily.RANKING_FACTOR_TRACE,
        ),
        PipelineStage.CONTEXT_CURATION: (ArtifactFamily.CONTEXT_BUNDLE,),
        PipelineStage.CANDIDATE_DESIGN: (ArtifactFamily.CANDIDATE_DESIGN,),
        PipelineStage.CANDIDATE_GENERATION: (ArtifactFamily.CANDIDATE_PATCH,),
        PipelineStage.FALSIFICATION: (ArtifactFamily.FALSIFICATION_REPORT,),
        PipelineStage.VERIFICATION: (ArtifactFamily.CANDIDATE_VERIFICATION,),
        PipelineStage.PROPOSAL_PACKAGING: (
            ArtifactFamily.CONFIDENCE_SHAPING_SUMMARY,
            ArtifactFamily.FORGEHQ_PROPOSAL,
            ArtifactFamily.FORGEHQ_EVIDENCE_BUNDLE,
        ),
    }
)


STAGE_OWNER: Final[Mapping[PipelineStage, WorkerName]] = MappingProxyType(
    {
        PipelineStage.SIGNAL_INTAKE: WorkerName.SIGNAL_ANALYST,
        PipelineStage.TARGET_RANKING: WorkerName.SIGNAL_ANALYST,
        PipelineStage.CONTEXT_CURATION: WorkerName.CONTEXT_CURATOR,
        PipelineStage.CANDIDATE_DESIGN: WorkerName.DESIGNER,
        PipelineStage.CANDIDATE_GENERATION: WorkerName.GENERATOR,
        PipelineStage.FALSIFICATION: WorkerName.CRITIC_FALSIFIER,
        PipelineStage.VERIFICATION: WorkerName.VERIFIER,
        PipelineStage.PROPOSAL_PACKAGING: WorkerName.PROPOSAL_ASSEMBLER,
    }
)
