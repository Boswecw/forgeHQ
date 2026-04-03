from enum import StrEnum
from types import MappingProxyType
from typing import Final, Mapping

from app.domain.artifacts.enums import ArtifactFamily


class WorkerName(StrEnum):
    SIGNAL_ANALYST = "signal_analyst"
    CONTEXT_CURATOR = "context_curator"
    DESIGNER = "designer"
    GENERATOR = "generator"
    CRITIC_FALSIFIER = "critic_falsifier"
    VERIFIER = "verifier"
    PROPOSAL_ASSEMBLER = "proposal_assembler"
    ORCHESTRATOR = "orchestrator"


# The critic lane must remain structurally independent from the generator lane.
WORKER_OWNERSHIP_REGISTRY: Final[Mapping[WorkerName, tuple[ArtifactFamily, ...]]] = MappingProxyType(
    {
        WorkerName.SIGNAL_ANALYST: (
            ArtifactFamily.SIGNAL_SNAPSHOT,
            ArtifactFamily.INTAKE_DIAGNOSTICS,
            ArtifactFamily.TARGET_RANKING,
            ArtifactFamily.RANKING_FACTOR_TRACE,
        ),
        WorkerName.CONTEXT_CURATOR: (ArtifactFamily.CONTEXT_BUNDLE,),
        WorkerName.DESIGNER: (ArtifactFamily.CANDIDATE_DESIGN,),
        WorkerName.GENERATOR: (ArtifactFamily.CANDIDATE_PATCH,),
        WorkerName.CRITIC_FALSIFIER: (ArtifactFamily.FALSIFICATION_REPORT,),
        WorkerName.VERIFIER: (ArtifactFamily.CANDIDATE_VERIFICATION,),
        WorkerName.PROPOSAL_ASSEMBLER: (
            ArtifactFamily.CONFIDENCE_SHAPING_SUMMARY,
            ArtifactFamily.FORGEHQ_PROPOSAL,
            ArtifactFamily.FORGEHQ_EVIDENCE_BUNDLE,
        ),
        WorkerName.ORCHESTRATOR: (),
    }
)
