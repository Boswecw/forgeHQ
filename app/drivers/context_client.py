"""context_client — call the context-runtime service to assemble a governed
context bundle for a code target.

context-runtime (PCC-conforming) is the engine behind the CONTEXT_CURATION
stage: it gathers candidate sources for a target file, runs precomputed-context-
core's ``assemble_context``, and serves a governed ``ContextBundleManifest`` plus
code-native payloads. forgeHQ consumes the admitted refs (and, when a generator
needs them, the payloads behind them).

Stdlib-only (urllib) per forgeHQ's standard-library-first contract — same posture
as ``healing_publisher``. Fail-closed: raises urllib errors on transport / non-2xx
so the caller never proceeds on a missing governed bundle.
"""
from __future__ import annotations

import json
import urllib.parse
import urllib.request

DEFAULT_CONTEXT_RUNTIME_URL = "http://127.0.0.1:8011"


def assemble_context_bundle(
    repo_id: str,
    repo_root: str,
    target_file: str,
    *,
    context_runtime_url: str = DEFAULT_CONTEXT_RUNTIME_URL,
    max_source_age_minutes: int | None = None,
    task_family: str = "code_fix",
    task_version: str = "v1",
    timeout: float = 15.0,
) -> dict:
    """POST a target to context-runtime and return the governed assemble result.

    The result carries ``context_bundle_id``, ``bundle_hash``, the PCC
    ``manifest``, and ``context_item_refs`` (== admitted ``payload_refs``).
    """
    payload: dict = {
        "repo_id": repo_id,
        "repo_root": repo_root,
        "target_file": target_file,
        "task_family": task_family,
        "task_version": task_version,
    }
    if max_source_age_minutes is not None:
        payload["max_source_age_minutes"] = max_source_age_minutes

    url = f"{context_runtime_url.rstrip('/')}/v1/context/assemble"
    body = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def fetch_payload(
    bundle_id: str,
    payload_ref: str,
    *,
    context_runtime_url: str = DEFAULT_CONTEXT_RUNTIME_URL,
    timeout: float = 15.0,
) -> dict:
    """Fetch one code-native payload behind an admitted ref.

    context-runtime fails closed (HTTP 409) if ``payload_ref`` is not in the
    bundle's admitted inventory — the same scope-escape guard the forgeHQ
    generator enforces, but at the source.
    """
    base = context_runtime_url.rstrip("/")
    ref_q = urllib.parse.quote(payload_ref, safe="")
    url = f"{base}/v1/context/{bundle_id}/payload?ref={ref_q}"
    request = urllib.request.Request(url, method="GET")
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))
