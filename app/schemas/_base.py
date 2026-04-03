from dataclasses import dataclass, field
from uuid import uuid4

from app.domain.artifacts.enums import ArtifactAuthorityPosture, ArtifactFamily
from app.domain.pipeline.enums import PipelineStage


def _artifact_id() -> str:
    return f"artifact-{uuid4().hex[:12]}"


@dataclass(frozen=True, slots=True)
class ArtifactStub:
    run_id: str
    artifact_family: ArtifactFamily
    stage: PipelineStage
    artifact_id: str = field(default_factory=_artifact_id)
    authority_posture: ArtifactAuthorityPosture = ArtifactAuthorityPosture.NON_AUTHORITATIVE
    placeholder: bool = True
    non_authoritative_notice: str = (
        "Non-authoritative placeholder artifact for bounded Phase 1 stage progression."
    )
    parent_artifact_ids: tuple[str, ...] = ()
    summary: str = "Phase 1 placeholder artifact."
