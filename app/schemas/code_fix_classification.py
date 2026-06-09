"""Code-fix classification contracts (the 'what' + its provenance).

CodeFixClassification.v1 — the resolved capability category for a code-fix job, with
full provenance (how it was classified, by whom, confidence, overrides). Drives the
routing cell NeuroForge learns best-model-per-category on, and the risk floor.

RiskFloorResolution.v1 — the auditable result of risk-floor inheritance
(max of explicit + primary-kind + secondary-kind floors) and the min tier it forces.

Plain frozen dataclasses (not pipeline ArtifactStubs): classification is metadata
attached to a job, not a pipeline-stage artifact.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum


class ClassificationMethod(StrEnum):
    DETERMINISTIC_RULE = "deterministic_rule"
    NEUROFORGE_CLASSIFIER = "neuroforge_classifier"
    AAR_DERIVED = "aar_derived"
    BUGCHECK_DERIVED = "bugcheck_derived"
    OPERATOR_ASSIGNED = "operator_assigned"
    RECLASSIFIED_AFTER_DIAGNOSIS = "reclassified_after_diagnosis"


@dataclass(frozen=True, slots=True)
class RiskFloorResolution:
    """How the effective risk (and forced min tier) was derived — fully auditable."""

    explicit_risk: str
    primary_kind: str
    primary_kind_floor: str
    secondary_kind_floors: tuple[tuple[str, str], ...]  # (kind, floor) pairs
    effective_risk: str
    min_tier: str | None
    rationale: str


@dataclass(frozen=True, slots=True)
class CodeFixClassification:
    """The resolved capability category for one code-fix job + provenance."""

    # The "what"
    family: str
    kind: str
    secondary_kinds: tuple[str, ...]
    language: str
    complexity: str
    routing_cell: str            # compose_key(family, kind, language, complexity)
    risk: str                    # effective risk (post-inheritance)
    min_tier: str | None         # forced floor (None = let the ladder decide)
    risk_resolution: RiskFloorResolution

    # Provenance
    classification_method: str = ClassificationMethod.DETERMINISTIC_RULE.value
    classifier_identity: str = "forgehq.code_fix_classifier"
    classifier_revision: str = "v1"
    confidence: float = 1.0
    classification_timestamp: str = ""
    taxonomy_version: str = ""

    # Lineage / overrides
    context_bundle_id: str | None = None
    previous_classification_id: str | None = None
    manual_overrides: tuple[str, ...] = ()
    override_actor: str | None = None
    override_reason: str | None = None
