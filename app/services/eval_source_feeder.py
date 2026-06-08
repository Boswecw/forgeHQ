"""Eval-family source feeder for forgeHQ Stage-1 signal intake.

Maps forge-eval and ForgeMath evaluation OUTPUTS into admissible forgeHQ source
refs for ``SignalIntakeService``:

  - forge-eval outputs -> ``forgeeval://`` (deterministic_evidence)
  - ForgeMath outputs  -> ``forgemath://`` (governed_math)

Policy (chosen): ALL evaluation outputs become signals; forgeHQ's intake and
reviewability decide downstream what is reviewable. forgeHQ never overwrites the
upstream authority — it only shapes reviewable candidates from these signals.

This feeder produces source refs only; the caller hands them to
``SignalIntakeService.admit_signals`` (or the orchestrator's ``run_from_signals``).
The actual enumeration of producer outputs (e.g. from the DataForge-Local lineage
graph) is supplied by the caller as ``EvalOutput`` records, keeping this feeder
deterministic and transport-free.
"""
from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from app.domain.signals.enums import is_admissible

FORGEEVAL_SCHEME = "forgeeval"
FORGEMATH_SCHEME = "forgemath"
_EVAL_SCHEMES = frozenset({FORGEEVAL_SCHEME, FORGEMATH_SCHEME})


@dataclass(frozen=True, slots=True)
class EvalOutput:
    """A forge-eval / ForgeMath lineage output to feed into forgeHQ intake.

    scheme: ``forgeeval`` (forge-eval) or ``forgemath`` (ForgeMath).
    output_type: the producer node type, e.g. ``forge_eval_evidence_bundle``,
        ``forge_eval_run``, ``forgemath_evaluation``, ``forgemath_output``,
        ``forgemath_runtime_admission``.
    output_id: the producer's stable output / lineage node id.
    """

    scheme: str
    output_type: str
    output_id: str

    def to_source_ref(self) -> str:
        if self.scheme not in _EVAL_SCHEMES:
            raise ValueError(f"unknown eval scheme: {self.scheme!r}")
        if not self.output_type or not self.output_id:
            raise ValueError("eval output requires non-empty output_type and output_id")
        return f"{self.scheme}://{self.output_type}/{self.output_id}"


class EvalSourceFeeder:
    """Builds admissible forgeHQ source refs from eval-family outputs."""

    @staticmethod
    def forgeeval_output(output_type: str, output_id: str) -> EvalOutput:
        return EvalOutput(FORGEEVAL_SCHEME, output_type, output_id)

    @staticmethod
    def forgemath_output(output_type: str, output_id: str) -> EvalOutput:
        return EvalOutput(FORGEMATH_SCHEME, output_type, output_id)

    def collect_source_refs(self, outputs: Iterable[EvalOutput]) -> tuple[str, ...]:
        """Map ALL eval-family outputs to forgeHQ source refs (chosen policy).

        Defensive: every produced ref must be admissible by scheme, otherwise the
        feeder fails closed rather than handing an inadmissible ref to intake
        (which would reject it). Order is preserved.
        """
        refs = tuple(output.to_source_ref() for output in outputs)
        inadmissible = tuple(ref for ref in refs if not is_admissible(ref))
        if inadmissible:
            raise ValueError(
                "feeder produced inadmissible refs (would be rejected at intake): "
                f"{inadmissible}"
            )
        return refs
