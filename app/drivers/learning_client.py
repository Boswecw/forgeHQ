"""learning_client — emit a CodeFixOutcome to NeuroForge's (shadow) model-outcome ingest.

Closes the feedback loop: a verified/accepted/applied (or failed) code-fix outcome is
POSTed to NeuroForge `POST /api/v1/learning/model-outcome`, which feeds the
(model, category) Category Champion Matrix so NeuroForge learns which model is best
for which kind of fix. Stdlib-only (urllib), same posture as the other forgeHQ drivers.

An outcome with no model_id (e.g. the deterministic stub generator) has nothing to
attribute, so emission is skipped — you can't teach the matrix a model from a fix no
model produced.
"""
from __future__ import annotations

import json
import urllib.request
from typing import Any

from app.schemas.code_fix_outcome import CodeFixOutcome

DEFAULT_NEUROFORGE_URL = "https://neuroforge-9lxc.onrender.com"


def outcome_to_request(outcome: CodeFixOutcome) -> dict[str, Any]:
    """Map a CodeFixOutcome to the model-outcome endpoint body."""
    return {
        "context_bundle_id": outcome.context_bundle_id,
        "model_id": outcome.model_id,
        "routing_cell": outcome.routing_cell,
        "reward": outcome.reward,
        "stage": outcome.stage,
        "tier": outcome.tier,
        "task_intent_id": outcome.task_intent_id,
        "source_system": outcome.source_system,
    }


def emit_model_outcome(
    outcome: CodeFixOutcome,
    *,
    neuroforge_url: str = DEFAULT_NEUROFORGE_URL,
    timeout: float = 10.0,
) -> dict[str, Any] | None:
    """POST one outcome to NeuroForge's learning ingest.

    Returns the endpoint response, or None when there is nothing to attribute
    (no model_id) — emission is skipped rather than failed.
    """
    if not outcome.model_id:
        return None
    url = f"{neuroforge_url.rstrip('/')}/api/v1/learning/model-outcome"
    body = json.dumps(outcome_to_request(outcome)).encode("utf-8")
    request = urllib.request.Request(
        url, data=body, headers={"Content-Type": "application/json"}, method="POST"
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))
