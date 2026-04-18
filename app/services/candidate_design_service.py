"""
Candidate design service for forgeHQ — Stage 4.

Validates and assembles a CandidateDesign artifact from a parent ContextBundle.
The design locks the scope boundary from the context bundle — the generator must
not exceed it.

Hard rules:
- Cannot design from a placeholder context bundle.
- All six required design fields must be non-empty.
- target_id in the design must match the context bundle's target_id.
- scope_boundary_statement is copied from the context bundle and locked.
- No generation is permitted before a valid CandidateDesign exists.
"""
from app.schemas.candidate_design import CandidateDesign
from app.schemas.context_bundle import ContextBundle


class DesignError(ValueError):
    """Raised when a CandidateDesign cannot be produced safely."""


class CandidateDesignService:
    """
    Produces a CandidateDesign artifact locked to a parent ContextBundle scope.

    Returns a CandidateDesign with placeholder=False.
    """

    def create_design(
        self,
        run_id: str,
        context_bundle: ContextBundle,
        change_hypothesis: str,
        intended_confidence_gain: str,
        targeted_behaviors: tuple[str, ...],
        oracle_strategy: str,
        disconfirming_checks: tuple[str, ...],
        failure_hypotheses: tuple[str, ...],
    ) -> CandidateDesign:
        """
        Assemble a CandidateDesign from a bounded ContextBundle.

        Raises DesignError if:
        - context_bundle is a placeholder
        - any of the six required design fields is empty
        """
        if context_bundle.placeholder:
            raise DesignError(
                "cannot create a design from a placeholder context bundle — "
                "run ContextBundleService first"
            )

        _require_nonempty(change_hypothesis, "change_hypothesis")
        _require_nonempty(intended_confidence_gain, "intended_confidence_gain")
        _require_nonempty(oracle_strategy, "oracle_strategy")

        if not targeted_behaviors:
            raise DesignError(
                "targeted_behaviors must contain at least one entry — "
                "a design without targeted behaviors has no measurable intent"
            )
        if not disconfirming_checks:
            raise DesignError(
                "disconfirming_checks must contain at least one entry — "
                "a design without disconfirming checks cannot be challenged"
            )
        if not failure_hypotheses:
            raise DesignError(
                "failure_hypotheses must contain at least one entry — "
                "a design without failure hypotheses cannot be falsified"
            )

        return CandidateDesign(
            run_id=run_id,
            placeholder=False,
            target_id=context_bundle.target_id,
            scope_boundary_statement=context_bundle.scope_boundary_statement,
            context_bundle_artifact_id=context_bundle.artifact_id,
            change_hypothesis=change_hypothesis,
            intended_confidence_gain=intended_confidence_gain,
            targeted_behaviors=targeted_behaviors,
            oracle_strategy=oracle_strategy,
            disconfirming_checks=disconfirming_checks,
            failure_hypotheses=failure_hypotheses,
            parent_artifact_ids=(context_bundle.artifact_id,),
            non_authoritative_notice=(
                "Non-authoritative candidate design. "
                "Does not claim deterministic upstream truth."
            ),
            summary=(
                f"Design for target '{context_bundle.target_id}': "
                f"{change_hypothesis[:80]!r}. "
                "Non-authoritative candidate proposal."
            ),
        )


def _require_nonempty(value: str, field_name: str) -> None:
    if not value.strip():
        raise DesignError(
            f"{field_name} must not be empty — "
            f"all six design fields are required before generation is permitted"
        )
