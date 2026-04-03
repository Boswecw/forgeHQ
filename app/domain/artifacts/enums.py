from dataclasses import dataclass
from enum import StrEnum
from types import MappingProxyType
from typing import Final, Mapping


class ArtifactFamily(StrEnum):
    SIGNAL_SNAPSHOT = "signal_snapshot"
    INTAKE_DIAGNOSTICS = "intake_diagnostics"
    TARGET_RANKING = "target_ranking"
    RANKING_FACTOR_TRACE = "ranking_factor_trace"
    CONTEXT_BUNDLE = "context_bundle"
    CANDIDATE_DESIGN = "candidate_design"
    CANDIDATE_PATCH = "candidate_patch"
    FALSIFICATION_REPORT = "falsification_report"
    CANDIDATE_VERIFICATION = "candidate_verification"
    CONFIDENCE_SHAPING_SUMMARY = "confidence_shaping_summary"
    FORGEHQ_PROPOSAL = "forgehq_proposal"
    FORGEHQ_EVIDENCE_BUNDLE = "forgehq_evidence_bundle"


class ArtifactAuthorityPosture(StrEnum):
    NON_AUTHORITATIVE = "non_authoritative"


class LineageLayer(StrEnum):
    DETERMINISTIC_EVIDENCE = "deterministic_evidence"
    NON_AUTHORITATIVE_PROPOSAL = "non_authoritative_proposal"
    OPERATOR_DECISION = "operator_decision"


@dataclass(frozen=True, slots=True)
class ArtifactFamilyDefinition:
    description: str
    required_for_reviewability_backbone: bool


ARTIFACT_FAMILY_REGISTRY: Final[Mapping[ArtifactFamily, ArtifactFamilyDefinition]] = MappingProxyType(
    {
        ArtifactFamily.SIGNAL_SNAPSHOT: ArtifactFamilyDefinition(
            description="Bounded snapshot of admitted source signals and source refs.",
            required_for_reviewability_backbone=True,
        ),
        ArtifactFamily.INTAKE_DIAGNOSTICS: ArtifactFamilyDefinition(
            description="Admission diagnostics captured during signal intake.",
            required_for_reviewability_backbone=False,
        ),
        ArtifactFamily.TARGET_RANKING: ArtifactFamilyDefinition(
            description="Governed ranking for the selected improvement target.",
            required_for_reviewability_backbone=True,
        ),
        ArtifactFamily.RANKING_FACTOR_TRACE: ArtifactFamilyDefinition(
            description="Explainability trace for ranking-factor contributions.",
            required_for_reviewability_backbone=False,
        ),
        ArtifactFamily.CONTEXT_BUNDLE: ArtifactFamilyDefinition(
            description="Bounded single-target context bundle with scope statement.",
            required_for_reviewability_backbone=True,
        ),
        ArtifactFamily.CANDIDATE_DESIGN: ArtifactFamilyDefinition(
            description="Design artifact that defines the bounded change hypothesis.",
            required_for_reviewability_backbone=True,
        ),
        ArtifactFamily.CANDIDATE_PATCH: ArtifactFamilyDefinition(
            description="Generated candidate artifact produced inside the approved scope.",
            required_for_reviewability_backbone=True,
        ),
        ArtifactFamily.FALSIFICATION_REPORT: ArtifactFamilyDefinition(
            description="Independent critic output that challenges the candidate.",
            required_for_reviewability_backbone=True,
        ),
        ArtifactFamily.CANDIDATE_VERIFICATION: ArtifactFamilyDefinition(
            description="Verification output that records observed gain and residual weakness.",
            required_for_reviewability_backbone=True,
        ),
        ArtifactFamily.CONFIDENCE_SHAPING_SUMMARY: ArtifactFamilyDefinition(
            description="Non-authoritative confidence summary for a candidate proposal.",
            required_for_reviewability_backbone=True,
        ),
        ArtifactFamily.FORGEHQ_PROPOSAL: ArtifactFamilyDefinition(
            description="Human-review package assembled from the required backbone artifacts.",
            required_for_reviewability_backbone=True,
        ),
        ArtifactFamily.FORGEHQ_EVIDENCE_BUNDLE: ArtifactFamilyDefinition(
            description="Optional supporting evidence bundle for downstream review surfaces.",
            required_for_reviewability_backbone=False,
        ),
    }
)


REQUIRED_REVIEWABILITY_BACKBONE: Final[tuple[ArtifactFamily, ...]] = tuple(
    family
    for family, definition in ARTIFACT_FAMILY_REGISTRY.items()
    if definition.required_for_reviewability_backbone
)


def enum_values(enum_cls: type[StrEnum]) -> tuple[str, ...]:
    return tuple(member.value for member in enum_cls)
