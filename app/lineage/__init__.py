"""ForgeLineage integration for forgeHQ (Phase 07).

Surfaces:
- ``emitter.ForgeHQLineageEmitter``: non-blocking producer of consumer-side
  forgeHQ lineage records (signal_intake, shaping_candidate, reviewability_result
  nodes; consumed/informed/required_review edges).
- ``reviewability.check_reviewability_lineage``: fail-closed governance check
  that blocks promotion of a proposal to REVIEWABLE if the upstream ForgeMath
  edge chain is missing, pending, stale, or has unknown causality.
"""

from app.lineage.emitter import (
    ForgeHQLineageEmitter,
    LineageEmissionStatus,
    NullLineageEmitter,
)
from app.lineage.reviewability import (
    LineageReviewabilityDecision,
    check_reviewability_lineage,
)

__all__ = [
    "ForgeHQLineageEmitter",
    "LineageEmissionStatus",
    "NullLineageEmitter",
    "LineageReviewabilityDecision",
    "check_reviewability_lineage",
]
