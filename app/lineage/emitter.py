"""forgeHQ consumer-side lineage emitter.

Emits the consumer-side chain:
  forgemath_output --consumed_by--> forgehq_signal_intake
  forgehq_signal_intake --informed--> forgehq_shaping_candidate
  forgehq_shaping_candidate --required_review--> forgehq_reviewability_result
"""

from __future__ import annotations

import logging
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


def _ensure_sdk_on_path() -> None:
    here = Path(__file__).resolve()
    candidates = [
        here.parents[4] / "contracts" / "forge_lineage" / "sdk",
        Path.home() / "Forge" / "ecosystem" / "contracts" / "forge_lineage" / "sdk",
    ]
    for c in candidates:
        if c.exists() and str(c) not in sys.path:
            sys.path.insert(0, str(c))
            return


_ensure_sdk_on_path()

from forge_lineage_sdk import LineageClient, LocalOutcome  # noqa: E402
from forge_lineage_sdk.builders import build_edge, build_envelope, build_node  # noqa: E402


@dataclass
class LineageEmissionStatus:
    signal_intake_node_id: str | None = None
    shaping_candidate_node_id: str | None = None
    reviewability_node_id: str | None = None
    consumed_by_edge_id: str | None = None
    informed_edge_id: str | None = None
    required_review_edge_id: str | None = None
    outcome: str = "lineage_missing"
    error: str | None = None


class ForgeHQLineageEmitter:
    WRITER_IDENTITY = "forgehq"
    SOURCE_SYSTEM = "forgehq"

    def __init__(self, client: LineageClient) -> None:
        self._client = client

    @classmethod
    def from_env(
        cls,
        *,
        base_url: str = "http://127.0.0.1:8005",
        writer_token: str = "local-forgehq",
    ) -> "ForgeHQLineageEmitter":
        return cls(
            LineageClient(
                base_url=base_url,
                writer_identity=cls.WRITER_IDENTITY,
                writer_token=writer_token,
            )
        )

    def emit_signal_intake_consumed(
        self,
        *,
        signal_intake_id: str,
        forgemath_output_node_id: str,
        source_output_id: str,
        source_payload_hash: str | None = None,
        ingested_at: str,
        trace_id: str | None = None,
    ) -> LineageEmissionStatus:
        """Emit forgehq_signal_intake node + consumed_by edge from a forgemath_output."""
        try:
            return self._emit_signal_intake(
                signal_intake_id=signal_intake_id,
                forgemath_output_node_id=forgemath_output_node_id,
                source_output_id=source_output_id,
                source_payload_hash=source_payload_hash,
                ingested_at=ingested_at,
                trace_id=trace_id,
            )
        except Exception as exc:  # noqa: BLE001
            logger.warning("forgehq signal_intake lineage emission raised", exc_info=exc)
            return LineageEmissionStatus(outcome="lineage_missing", error=f"{type(exc).__name__}: {exc}")

    def emit_shaping_candidate(
        self,
        *,
        candidate_id: str,
        signal_intake_node_id: str,
        proposed_at: str,
        summary: str | None = None,
        trace_id: str | None = None,
    ) -> LineageEmissionStatus:
        try:
            return self._emit_shaping_candidate(
                candidate_id=candidate_id,
                signal_intake_node_id=signal_intake_node_id,
                proposed_at=proposed_at,
                summary=summary,
                trace_id=trace_id,
            )
        except Exception as exc:  # noqa: BLE001
            logger.warning("forgehq shaping_candidate lineage emission raised", exc_info=exc)
            return LineageEmissionStatus(outcome="lineage_missing", error=f"{type(exc).__name__}: {exc}")

    def emit_reviewability_result(
        self,
        *,
        reviewability_id: str,
        candidate_node_id: str,
        candidate_id: str,
        state: str,
        decided_at: str,
        block_reason_class: str | None = None,
        lineage_availability: str | None = None,
        trace_id: str | None = None,
    ) -> LineageEmissionStatus:
        try:
            return self._emit_reviewability(
                reviewability_id=reviewability_id,
                candidate_node_id=candidate_node_id,
                candidate_id=candidate_id,
                state=state,
                decided_at=decided_at,
                block_reason_class=block_reason_class,
                lineage_availability=lineage_availability,
                trace_id=trace_id,
            )
        except Exception as exc:  # noqa: BLE001
            logger.warning("forgehq reviewability lineage emission raised", exc_info=exc)
            return LineageEmissionStatus(outcome="lineage_missing", error=f"{type(exc).__name__}: {exc}")

    # ---- internals ----

    def _emit_signal_intake(
        self,
        *,
        signal_intake_id: str,
        forgemath_output_node_id: str,
        source_output_id: str,
        source_payload_hash: str | None,
        ingested_at: str,
        trace_id: str | None,
    ) -> LineageEmissionStatus:
        trace = trace_id or f"trace:forgehq:{signal_intake_id}"
        payload: dict[str, Any] = {
            "schema_version": "forgehq_signal_intake.v1",
            "signal_intake_id": signal_intake_id,
            "ingested_at": ingested_at,
            "source_output_id": source_output_id,
        }
        if source_payload_hash:
            payload["source_payload_hash"] = source_payload_hash
        intake_node = build_node(
            node_type="forgehq_signal_intake",
            payload_schema_id="forgehq_signal_intake",
            payload_schema_version="v1",
            payload=payload,
            source_system=self.SOURCE_SYSTEM,
            source_component="forgehq/signal_intake",
            trace_id=trace,
            writer_identity=self.WRITER_IDENTITY,
            stable_source_id=f"forgehq:intake:{signal_intake_id}",
        )
        consumed_by_edge = build_edge(
            source_node_id=forgemath_output_node_id,
            target_node_id=intake_node["node_id"],
            edge_type="consumed_by",
            causality_class="deterministic",
            effect_class="shaping",
            trace_id=trace,
            writer_identity=self.WRITER_IDENTITY,
            created_by_system=self.SOURCE_SYSTEM,
            stable_source_id=f"{forgemath_output_node_id}->{intake_node['node_id']}",
        )
        envelope = build_envelope(
            writer_identity=self.WRITER_IDENTITY,
            trace_id=trace,
            nodes=[intake_node],
            edges=[consumed_by_edge],
        )
        result = self._client.emit_envelope(envelope)
        if result.outcome in (LocalOutcome.accepted, LocalOutcome.accepted_duplicate):
            return LineageEmissionStatus(
                signal_intake_node_id=intake_node["node_id"],
                consumed_by_edge_id=consumed_by_edge["edge_id"],
                outcome="lineage_available",
            )
        if result.outcome == LocalOutcome.pending:
            return LineageEmissionStatus(
                signal_intake_node_id=intake_node["node_id"],
                consumed_by_edge_id=consumed_by_edge["edge_id"],
                outcome="lineage_pending",
            )
        return LineageEmissionStatus(
            signal_intake_node_id=intake_node["node_id"],
            outcome="lineage_degraded",
            error=(result.error.message if result.error else f"non-accept: {result.outcome}"),
        )

    def _emit_shaping_candidate(
        self,
        *,
        candidate_id: str,
        signal_intake_node_id: str,
        proposed_at: str,
        summary: str | None,
        trace_id: str | None,
    ) -> LineageEmissionStatus:
        trace = trace_id or f"trace:forgehq:{candidate_id}"
        payload: dict[str, Any] = {
            "schema_version": "forgehq_shaping_candidate.v1",
            "candidate_id": candidate_id,
            "proposed_at": proposed_at,
        }
        if summary:
            payload["summary"] = summary
        candidate_node = build_node(
            node_type="forgehq_shaping_candidate",
            payload_schema_id="forgehq_shaping_candidate",
            payload_schema_version="v1",
            payload=payload,
            source_system=self.SOURCE_SYSTEM,
            source_component="forgehq/shaping",
            trace_id=trace,
            writer_identity=self.WRITER_IDENTITY,
            stable_source_id=f"forgehq:candidate:{candidate_id}",
        )
        informed_edge = build_edge(
            source_node_id=signal_intake_node_id,
            target_node_id=candidate_node["node_id"],
            edge_type="informed",
            causality_class="derived",
            effect_class="shaping",
            trace_id=trace,
            writer_identity=self.WRITER_IDENTITY,
            created_by_system=self.SOURCE_SYSTEM,
            stable_source_id=f"{signal_intake_node_id}->{candidate_node['node_id']}",
        )
        envelope = build_envelope(
            writer_identity=self.WRITER_IDENTITY,
            trace_id=trace,
            nodes=[candidate_node],
            edges=[informed_edge],
        )
        result = self._client.emit_envelope(envelope)
        if result.outcome in (LocalOutcome.accepted, LocalOutcome.accepted_duplicate):
            return LineageEmissionStatus(
                shaping_candidate_node_id=candidate_node["node_id"],
                informed_edge_id=informed_edge["edge_id"],
                outcome="lineage_available",
            )
        return LineageEmissionStatus(
            shaping_candidate_node_id=candidate_node["node_id"],
            outcome="lineage_degraded",
            error=(result.error.message if result.error else f"non-accept: {result.outcome}"),
        )

    def _emit_reviewability(
        self,
        *,
        reviewability_id: str,
        candidate_node_id: str,
        candidate_id: str,
        state: str,
        decided_at: str,
        block_reason_class: str | None,
        lineage_availability: str | None,
        trace_id: str | None,
    ) -> LineageEmissionStatus:
        trace = trace_id or f"trace:forgehq:{reviewability_id}"
        payload: dict[str, Any] = {
            "schema_version": "forgehq_reviewability_result.v1",
            "reviewability_id": reviewability_id,
            "candidate_id": candidate_id,
            "state": state,
            "decided_at": decided_at,
        }
        if block_reason_class:
            payload["block_reason_class"] = block_reason_class
        if lineage_availability:
            payload["lineage_availability"] = lineage_availability
        result_node = build_node(
            node_type="forgehq_reviewability_result",
            payload_schema_id="forgehq_reviewability_result",
            payload_schema_version="v1",
            payload=payload,
            source_system=self.SOURCE_SYSTEM,
            source_component="forgehq/reviewability",
            trace_id=trace,
            writer_identity=self.WRITER_IDENTITY,
            stable_source_id=f"forgehq:reviewability:{reviewability_id}",
        )
        review_edge = build_edge(
            source_node_id=candidate_node_id,
            target_node_id=result_node["node_id"],
            edge_type="required_review",
            causality_class="derived",
            effect_class="advisory",
            trace_id=trace,
            writer_identity=self.WRITER_IDENTITY,
            created_by_system=self.SOURCE_SYSTEM,
            stable_source_id=f"{candidate_node_id}->{result_node['node_id']}",
        )
        envelope = build_envelope(
            writer_identity=self.WRITER_IDENTITY,
            trace_id=trace,
            nodes=[result_node],
            edges=[review_edge],
        )
        out = self._client.emit_envelope(envelope)
        if out.outcome in (LocalOutcome.accepted, LocalOutcome.accepted_duplicate):
            return LineageEmissionStatus(
                reviewability_node_id=result_node["node_id"],
                required_review_edge_id=review_edge["edge_id"],
                outcome="lineage_available",
            )
        return LineageEmissionStatus(
            reviewability_node_id=result_node["node_id"],
            outcome="lineage_degraded",
            error=(out.error.message if out.error else f"non-accept: {out.outcome}"),
        )


class NullLineageEmitter:
    def emit_signal_intake_consumed(self, **_kwargs: Any) -> LineageEmissionStatus:
        return LineageEmissionStatus(outcome="lineage_missing", error="emitter_disabled")

    def emit_shaping_candidate(self, **_kwargs: Any) -> LineageEmissionStatus:
        return LineageEmissionStatus(outcome="lineage_missing", error="emitter_disabled")

    def emit_reviewability_result(self, **_kwargs: Any) -> LineageEmissionStatus:
        return LineageEmissionStatus(outcome="lineage_missing", error="emitter_disabled")
