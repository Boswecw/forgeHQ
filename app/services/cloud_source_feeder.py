"""Cloud-proposal source feeder for forgeHQ Stage-1 signal intake.

Maps ForgeCommand cloud proposals (the FC-server cloud diagnostics ->
recommendations subsystem: ``cloud_proposals``) into admissible forgeHQ source
refs under the ``cloud://`` scheme (a weak / advisory signal — see
``app.domain.signals.enums``). This gives forgeHQ a cloud feed symmetric to the
eval-family feeder, so cloud issues flow into the same intake as forge-eval /
ForgeMath.

Transport-free: the caller supplies ``CloudProposal`` records (e.g. read from the
FC-server cloud-proposals API or handoffs), keeping this feeder deterministic.
forgeHQ stays non-authoritative — a cloud proposal is a weak advisory signal,
never deterministic truth.
"""
from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from app.domain.signals.enums import is_admissible

CLOUD_SCHEME = "cloud"


@dataclass(frozen=True, slots=True)
class CloudProposal:
    """A ForgeCommand cloud proposal to feed into forgeHQ intake.

    proposal_id: the FC-server ``cloud_proposals.proposal_id``.
    service: the target service the proposal concerns (e.g. ``neuroforge``);
        encoded as the ref category. Defaults to ``unknown``.
    """

    proposal_id: str
    service: str = "unknown"

    def to_source_ref(self) -> str:
        if not self.proposal_id:
            raise ValueError("cloud proposal requires a non-empty proposal_id")
        service = self.service or "unknown"
        return f"{CLOUD_SCHEME}://{service}/{self.proposal_id}"


class CloudSourceFeeder:
    """Builds admissible forgeHQ source refs from FC-server cloud proposals."""

    @staticmethod
    def proposal(proposal_id: str, service: str = "unknown") -> CloudProposal:
        return CloudProposal(proposal_id=proposal_id, service=service)

    def collect_source_refs(self, proposals: Iterable[CloudProposal]) -> tuple[str, ...]:
        """Map cloud proposals to admissible forgeHQ source refs (order preserved).

        Defensive: fails closed if any produced ref is inadmissible by scheme.
        """
        refs = tuple(proposal.to_source_ref() for proposal in proposals)
        inadmissible = tuple(ref for ref in refs if not is_admissible(ref))
        if inadmissible:
            raise ValueError(
                "feeder produced inadmissible refs (would be rejected at intake): "
                f"{inadmissible}"
            )
        return refs
