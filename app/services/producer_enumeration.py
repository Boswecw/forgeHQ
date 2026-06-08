"""Producer enumeration mappers (transport-free) for the forgeHQ feed.

Pure functions that normalise producer OUTPUT records into feeder inputs:

  - DataForge-Local lineage node dicts -> ``EvalOutput`` (forge-eval / ForgeMath)
  - ForgeCommand cloud-proposal records -> ``CloudProposal``

These are the *enumeration* half of the feed (forgeHQ feed plan, P2): a driver
supplies the records — read from the DataForge-Local lineage list surface
(``GET /api/v1/lineage/nodes?node_type=...``) or the FC cloud-proposals API —
and these mappers turn them into ``EvalSourceFeeder`` / ``CloudSourceFeeder``
inputs. Kept transport-free per forgeHQ's phase-bounded, non-authoritative
doctrine: no HTTP / persistence here, only deterministic mapping.
"""
from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

from app.services.cloud_source_feeder import CloudProposal
from app.services.eval_source_feeder import (
    FORGEEVAL_SCHEME,
    FORGEMATH_SCHEME,
    EvalOutput,
)

# forge-eval / ForgeMath lineage node_type prefixes (forge_eval_run,
# forge_eval_evidence_bundle, forgemath_evaluation, forgemath_output,
# forgemath_runtime_admission, ...).
_FORGEEVAL_NODE_PREFIX = "forge_eval_"
_FORGEMATH_NODE_PREFIX = "forgemath_"


def lineage_node_to_eval_output(node: Mapping[str, Any]) -> EvalOutput | None:
    """Map a lineage node dict to an EvalOutput.

    Returns None if the node is not a forge-eval / ForgeMath producer output, or
    is missing ``node_type`` / ``node_id``.
    """
    node_type = str(node.get("node_type") or "")
    node_id = str(node.get("node_id") or "")
    if not node_type or not node_id:
        return None
    if node_type.startswith(_FORGEEVAL_NODE_PREFIX):
        return EvalOutput(FORGEEVAL_SCHEME, node_type, node_id)
    if node_type.startswith(_FORGEMATH_NODE_PREFIX):
        return EvalOutput(FORGEMATH_SCHEME, node_type, node_id)
    return None


def eval_outputs_from_lineage(
    nodes: Iterable[Mapping[str, Any]],
) -> tuple[EvalOutput, ...]:
    """Map a batch of lineage nodes to EvalOutputs, skipping non-eval nodes."""
    mapped = (lineage_node_to_eval_output(node) for node in nodes)
    return tuple(output for output in mapped if output is not None)


def cloud_record_to_proposal(record: Mapping[str, Any]) -> CloudProposal | None:
    """Map an FC cloud-proposal record to a CloudProposal.

    Returns None if the record has no ``proposal_id``.
    """
    proposal_id = str(record.get("proposal_id") or "")
    if not proposal_id:
        return None
    service = str(record.get("service") or "unknown")
    return CloudProposal(proposal_id=proposal_id, service=service)


def cloud_proposals_from_records(
    records: Iterable[Mapping[str, Any]],
) -> tuple[CloudProposal, ...]:
    """Map a batch of cloud-proposal records to CloudProposals, skipping
    records without a proposal_id."""
    mapped = (cloud_record_to_proposal(record) for record in records)
    return tuple(proposal for proposal in mapped if proposal is not None)
