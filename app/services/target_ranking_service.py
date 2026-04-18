"""
Target ranking service for forgeHQ — Stage 2.

Scores candidate improvement targets from admitted signals and produces
a TargetRanking + RankingFactorTrace pair with full explainability.

Hard rules:
- Cannot rank from a placeholder signal snapshot.
- Every ranking factor source_ref must appear in the snapshot's admitted refs.
- At least one ranking factor is required.
- Deterministic factors (is_deterministic=True) receive 2× weight so that
  ForgeEval/ForgeMath evidence is structurally privileged over weak signals.
- All output is non-authoritative — does not overwrite upstream truth.
"""
from app.schemas.ranking_factor_trace import RankingFactor, RankingFactorTrace
from app.schemas.signal_snapshot import SignalSnapshot
from app.schemas.target_ranking import TargetRanking


class RankingError(ValueError):
    """Raised when target ranking cannot proceed safely."""


class TargetRankingService:
    """
    Ranks a single improvement target from admitted signals.

    Returns (TargetRanking, RankingFactorTrace) with placeholder=False.
    """

    def rank_target(
        self,
        run_id: str,
        target_id: str,
        signal_snapshot: SignalSnapshot,
        ranking_factors: tuple[RankingFactor, ...],
    ) -> tuple[TargetRanking, RankingFactorTrace]:
        """
        Produce a non-authoritative ranking for one target.

        Raises RankingError if the snapshot is a placeholder, no factors are
        provided, or any factor source ref is not in the snapshot's admitted set.
        """
        if not target_id.strip():
            raise RankingError("target_id must not be empty")

        if signal_snapshot.placeholder:
            raise RankingError(
                "cannot rank targets from a placeholder signal snapshot — "
                "run SignalIntakeService first"
            )

        if not ranking_factors:
            raise RankingError(
                "at least one ranking factor is required — "
                "ranking without factors produces no explainability"
            )

        admitted_refs = set(signal_snapshot.admitted_source_refs)
        for factor in ranking_factors:
            if factor.source_ref not in admitted_refs:
                raise RankingError(
                    f"ranking factor '{factor.factor_name}' references source ref "
                    f"'{factor.source_ref}' which is not in the admitted signal snapshot"
                )

        composite_score = _compute_composite_score(ranking_factors)

        trace = RankingFactorTrace(
            run_id=run_id,
            placeholder=False,
            target_id=target_id,
            factors=ranking_factors,
            composite_score=composite_score,
            parent_artifact_ids=(signal_snapshot.artifact_id,),
            non_authoritative_notice=(
                "Non-authoritative ranking factor trace. "
                "Does not claim deterministic upstream truth."
            ),
            summary=(
                f"Ranking trace for target '{target_id}': "
                f"composite_score={composite_score:.3f}, "
                f"{len(ranking_factors)} factor(s)."
            ),
        )

        ranking = TargetRanking(
            run_id=run_id,
            placeholder=False,
            ranked_target_id=target_id,
            composite_score=composite_score,
            ranking_trace_artifact_id=trace.artifact_id,
            parent_artifact_ids=(signal_snapshot.artifact_id,),
            non_authoritative_notice=(
                "Non-authoritative target ranking. "
                "Does not claim deterministic upstream truth."
            ),
            summary=(
                f"Target '{target_id}' ranked with composite_score={composite_score:.3f}. "
                "Non-authoritative candidate selection."
            ),
        )

        return ranking, trace


def _compute_composite_score(factors: tuple[RankingFactor, ...]) -> float:
    """
    Weighted average of normalized factor scores.

    Deterministic factors (from ForgeEval/ForgeMath) receive 2× weight to
    structurally privilege deterministic evidence over weak signals.
    """
    total_weight = 0.0
    weighted_sum = 0.0
    for factor in factors:
        weight = 2.0 if factor.is_deterministic else 1.0
        weighted_sum += factor.normalized_score * weight
        total_weight += weight
    return weighted_sum / total_weight if total_weight > 0.0 else 0.0
