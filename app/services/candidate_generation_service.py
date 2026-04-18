"""
Candidate generation service for forgeHQ — Stage 5.

Enforces design-before-generation and scope adherence. A patch is only permitted
when a valid, non-placeholder CandidateDesign exists and all modified refs fall
within the parent ContextBundle's admitted context_item_refs.

Hard rules:
- Cannot generate from a placeholder design.
- Cannot generate from a placeholder context bundle.
- design.target_id must match context_bundle.target_id.
- Every modified ref must appear in context_bundle.context_item_refs.
  If the context bundle has items and the generator attempts to touch a ref
  outside that set, generation fails closed with GenerationScopeError.
  If the context bundle has zero items, modified_refs must also be empty.
- The adapter boundary is intentionally not wired in Phase 3.
  This service validates scope and produces the CandidatePatch envelope;
  actual diff/change content is a Phase 5 concern.
"""
from app.schemas.candidate_design import CandidateDesign
from app.schemas.candidate_patch import CandidatePatch
from app.schemas.context_bundle import ContextBundle


class GenerationScopeError(ValueError):
    """Raised when generation would violate the scope boundary — fail closed."""


class CandidateGenerationService:
    """
    Produces a CandidatePatch from a validated CandidateDesign.

    Enforces design existence and scope adherence before emitting a patch.
    Returns a CandidatePatch with placeholder=False and scope_adherence_verified=True.
    """

    def generate_patch(
        self,
        run_id: str,
        candidate_design: CandidateDesign,
        context_bundle: ContextBundle,
        modified_refs: tuple[str, ...],
    ) -> CandidatePatch:
        """
        Generate a bounded candidate patch from a valid design.

        Raises GenerationScopeError if:
        - candidate_design is a placeholder
        - context_bundle is a placeholder
        - design target_id does not match context bundle target_id
        - any modified ref is outside the context bundle's admitted items
        - context bundle has zero items but modified_refs is non-empty
        """
        if candidate_design.placeholder:
            raise GenerationScopeError(
                "cannot generate a patch from a placeholder design — "
                "run CandidateDesignService first"
            )

        if context_bundle.placeholder:
            raise GenerationScopeError(
                "cannot generate a patch against a placeholder context bundle — "
                "run ContextBundleService first"
            )

        if candidate_design.target_id != context_bundle.target_id:
            raise GenerationScopeError(
                f"design target_id '{candidate_design.target_id}' does not match "
                f"context bundle target_id '{context_bundle.target_id}' — "
                "scope escape rejected"
            )

        admitted = set(context_bundle.context_item_refs)

        if not admitted and modified_refs:
            raise GenerationScopeError(
                f"context bundle has zero admitted items but generator attempted "
                f"to modify {len(modified_refs)} ref(s) — scope escape rejected"
            )

        out_of_scope = tuple(ref for ref in modified_refs if ref not in admitted)
        if out_of_scope:
            raise GenerationScopeError(
                f"generator attempted to modify {len(out_of_scope)} ref(s) outside "
                f"the admitted context bundle scope: {out_of_scope} — "
                "fail closed on scope escape"
            )

        return CandidatePatch(
            run_id=run_id,
            placeholder=False,
            design_artifact_id=candidate_design.artifact_id,
            modified_refs=modified_refs,
            scope_adherence_verified=True,
            parent_artifact_ids=(candidate_design.artifact_id,),
            non_authoritative_notice=(
                "Non-authoritative candidate patch. "
                "Does not claim deterministic upstream truth."
            ),
            summary=(
                f"Candidate patch for target '{candidate_design.target_id}': "
                f"{len(modified_refs)} ref(s) modified within bounded scope. "
                "Non-authoritative — requires falsification and verification."
            ),
        )
