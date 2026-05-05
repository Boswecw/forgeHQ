"""forgeHQ reviewability lineage enforcement (Phase 07).

Per ``09_PHASE_07_FORGEMATH_TO_FORGEHQ.md``:

> forgeHQ must not mark a proposal reviewable if the required upstream
> ForgeMath ImpactEdge is missing or invalid.

The check looks up the ``consumed_by`` edge from the cited forgemath_output
node to the forgehq_signal_intake node. Failure modes:
- forgemath_output node missing
- forgehq_signal_intake node missing
- consumed_by edge missing
- edge pending / stale / superseded
- causality_class=unknown
- source payload hash drift
- DataForge unreachable -> fail closed
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import httpx


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

from forge_lineage_sdk.enforcement import (  # noqa: E402
    EdgeRequirement,
    enforce_edge_for_promotion,
)


@dataclass
class LineageReviewabilityDecision:
    allowed: bool
    availability: str
    reason_class: str | None
    reason_message: str | None
    edge: dict[str, Any] | None = None


def check_reviewability_lineage(
    *,
    forgemath_output_node_id: str,
    forgehq_signal_intake_node_id: str,
    expected_source_payload_hash: str | None = None,
    base_url: str = "http://127.0.0.1:8005",
    http_client: httpx.Client | None = None,
) -> LineageReviewabilityDecision:
    """Look up the source/target nodes and the ``consumed_by`` edge, then
    apply the SDK enforcement rule. Returns ``allowed=False`` if anything is
    wrong. On transport failure, returns ``allowed=False, availability="lineage_missing"``.
    """
    client = http_client
    owns_client = False
    if client is None:
        client = httpx.Client(base_url=base_url, timeout=5.0)
        owns_client = True
    try:
        try:
            source_resp = client.get(f"/api/v1/lineage/nodes/{forgemath_output_node_id}")
            target_resp = client.get(f"/api/v1/lineage/nodes/{forgehq_signal_intake_node_id}")
        except httpx.HTTPError as exc:
            return LineageReviewabilityDecision(
                allowed=False,
                availability="lineage_missing",
                reason_class="storage_error",
                reason_message=f"lineage transport failure: {exc!r}",
            )

        source = source_resp.json() if source_resp.status_code == 200 else None
        target = target_resp.json() if target_resp.status_code == 200 else None

        edge_record: dict[str, Any] | None = None
        if source is not None:
            try:
                down_resp = client.get(
                    f"/api/v1/lineage/nodes/{forgemath_output_node_id}/downstream",
                    params={"max_depth": 1},
                )
                if down_resp.status_code == 200:
                    body = down_resp.json()
                    for e in body.get("edges", []):
                        if (
                            e.get("source_node_id") == forgemath_output_node_id
                            and e.get("target_node_id") == forgehq_signal_intake_node_id
                            and e.get("edge_type") == "consumed_by"
                        ):
                            edge_record = e
                            break
            except httpx.HTTPError as exc:
                return LineageReviewabilityDecision(
                    allowed=False,
                    availability="lineage_missing",
                    reason_class="storage_error",
                    reason_message=f"lineage transport failure: {exc!r}",
                )

        result = enforce_edge_for_promotion(
            requirement=EdgeRequirement(
                source_node_id=forgemath_output_node_id,
                target_node_id=forgehq_signal_intake_node_id,
                edge_type="consumed_by",
                expected_source_payload_hash=expected_source_payload_hash,
                forbid_unknown_causality=True,
            ),
            source_node=source,
            target_node=target,
            edge=edge_record,
        )
        return LineageReviewabilityDecision(
            allowed=result.allowed,
            availability=result.availability,
            reason_class=result.reason_class,
            reason_message=result.reason_message,
            edge=result.edge,
        )
    finally:
        if owns_client:
            client.close()
