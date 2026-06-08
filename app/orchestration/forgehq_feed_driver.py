"""forgeHQ feed driver — enumerate -> feed -> run (transport-free).

Ties the feed plan together (P1 feeders + P2 enumeration + P3 real intake): given
producer OUTPUT records — DataForge-Local lineage nodes (forge-eval / ForgeMath)
and ForgeCommand cloud-proposal records — enumerate them into feeder inputs,
build admissible source refs, and drive a shaping run with REAL signal intake.

The shaping stages past intake stay on the placeholder path until the
proposal-shaping intelligence phase (feed plan P4 de-noop). Transport-free per
forgeHQ doctrine: a caller supplies the records (e.g. read from the
DataForge-Local lineage list surface or the FC cloud-proposals API); this driver
performs no HTTP / persistence and mints no upstream truth.
"""
from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

from app.orchestration.forgehq_orchestrator import ForgeHQOrchestrator
from app.schemas.shaping_run import ShapingRun
from app.services.cloud_source_feeder import CloudSourceFeeder
from app.services.eval_source_feeder import EvalSourceFeeder
from app.services.producer_enumeration import (
    cloud_proposals_from_records,
    eval_outputs_from_lineage,
)


class ForgeHQFeedDriver:
    """Drives a fed shaping run from producer output records."""

    def __init__(self) -> None:
        self._orchestrator = ForgeHQOrchestrator()
        self._eval_feeder = EvalSourceFeeder()
        self._cloud_feeder = CloudSourceFeeder()

    def collect_source_refs(
        self,
        *,
        lineage_nodes: Iterable[Mapping[str, Any]] = (),
        cloud_records: Iterable[Mapping[str, Any]] = (),
    ) -> tuple[str, ...]:
        """Enumerate + feed: producer records -> admissible source refs.

        forge-eval / ForgeMath lineage nodes first (deterministic evidence /
        governed math), then cloud proposals (weak advisory).
        """
        eval_refs = self._eval_feeder.collect_source_refs(
            eval_outputs_from_lineage(lineage_nodes)
        )
        cloud_refs = self._cloud_feeder.collect_source_refs(
            cloud_proposals_from_records(cloud_records)
        )
        return tuple(eval_refs) + tuple(cloud_refs)

    def run(
        self,
        run_id: str,
        *,
        lineage_nodes: Iterable[Mapping[str, Any]] = (),
        cloud_records: Iterable[Mapping[str, Any]] = (),
    ) -> ShapingRun:
        """Enumerate -> feed -> run_from_signals (real intake).

        Fails closed (NoAdmittedSourcesError) if no admissible source ref results
        from the supplied records.
        """
        source_refs = self.collect_source_refs(
            lineage_nodes=lineage_nodes, cloud_records=cloud_records
        )
        return self._orchestrator.run_from_signals(run_id, source_refs)
