"""
Context bundle service for forgeHQ — Stage 3.

Builds a bounded single-target context bundle from a ranked target artifact.

Hard rules:
- Cannot bundle from a placeholder target ranking.
- target_id must match the ranking's ranked_target_id exactly.
- scope_boundary_statement must not be empty.
- context_item_refs must not exceed SCOPE_MAX_ITEMS (fail closed).
- context_item_refs must not contain duplicates.
- All output is non-authoritative — does not overwrite upstream truth.
"""
from typing import Final

from app.schemas.context_bundle import ContextBundle
from app.schemas.target_ranking import TargetRanking

SCOPE_MAX_ITEMS: Final = 50


class ScopeEscapeError(ValueError):
    """Raised when scope policy is violated — fail closed."""


class ContextBundleService:
    """
    Produces a bounded single-target ContextBundle from a ranked target.

    Returns a ContextBundle with placeholder=False and explicit scope boundary.
    """

    def __init__(self, max_items: int = SCOPE_MAX_ITEMS) -> None:
        self._max_items = max_items

    def build_context_bundle(
        self,
        run_id: str,
        target_id: str,
        target_ranking: TargetRanking,
        context_item_refs: tuple[str, ...],
        scope_boundary_statement: str,
    ) -> ContextBundle:
        """
        Build a bounded context bundle for one ranked target.

        Raises ScopeEscapeError if:
        - scope_boundary_statement is empty
        - target_ranking is a placeholder
        - target_id does not match the ranking
        - context_item_refs exceed the max items policy
        - context_item_refs contain duplicates
        """
        if not scope_boundary_statement.strip():
            raise ScopeEscapeError(
                "scope_boundary_statement must not be empty — "
                "every context bundle requires an explicit scope boundary"
            )

        if target_ranking.placeholder:
            raise ScopeEscapeError(
                "cannot build context bundle from a placeholder target ranking — "
                "run TargetRankingService first"
            )

        if target_id != target_ranking.ranked_target_id:
            raise ScopeEscapeError(
                f"target_id '{target_id}' does not match ranking target "
                f"'{target_ranking.ranked_target_id}' — scope escape rejected"
            )

        if len(context_item_refs) > self._max_items:
            raise ScopeEscapeError(
                f"context scope exceeds policy: {len(context_item_refs)} items "
                f"exceeds max {self._max_items} — fail closed on scope escape"
            )

        if len(context_item_refs) != len(set(context_item_refs)):
            raise ScopeEscapeError(
                "context_item_refs must not contain duplicates — "
                "duplicate items are a scope integrity violation"
            )

        return ContextBundle(
            run_id=run_id,
            placeholder=False,
            target_id=target_id,
            scope_boundary_statement=scope_boundary_statement,
            scope_class="bounded_single_target",
            context_item_refs=context_item_refs,
            parent_artifact_ids=(target_ranking.artifact_id,),
            non_authoritative_notice=(
                "Non-authoritative context bundle. "
                "Does not claim deterministic upstream truth."
            ),
            summary=(
                f"Context bundle for target '{target_id}': "
                f"{len(context_item_refs)} item(s), bounded single-target scope."
            ),
        )
