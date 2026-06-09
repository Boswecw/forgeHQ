"""pact_client — invoke the pact (PAC) verification runtime in-process.

pact is the deterministic grounded-packet verification runtime. The self-healing
VERIFICATION stage delegates to it: given a candidate's grounding plus the
governed context bundle handle, pact compiles a schema-valid, replay-deterministic
packet + receipt that are BOUND to the bundle — the same context_bundle_id /
bundle_hash are echoed back, and packet/receipt identity changes if the bundle
changes. That bundle-bound receipt is the verification evidence a proposal carries.

pact is a sibling repo. Resolve its root via the PACT_ROOT env var, else the
ecosystem-relative ``../../pact`` (from ``ecosystem/local-systems/forgeHQ``), add
it to sys.path, and call ``execute_slice_07``. Fail-closed: raises
PactUnavailableError if pact cannot be located or imported, so a verification
never silently no-ops.

Both forgeHQ and pact are Python in one ecosystem, so this is an in-process call,
not HTTP — pact is consumed as-is and is not modified.
"""
from __future__ import annotations

import os
import sys
from functools import lru_cache
from pathlib import Path
from typing import Any, Callable


class PactUnavailableError(RuntimeError):
    """Raised when the pact runtime cannot be located or imported — fail closed."""


def _resolve_pact_root() -> Path:
    env = os.environ.get("PACT_ROOT")
    if env and env.strip():
        root = Path(env).expanduser().resolve()
    else:
        # forgeHQ/app/drivers/pact_client.py
        #   parents[2]=forgeHQ  parents[3]=local-systems  parents[4]=ecosystem
        root = Path(__file__).resolve().parents[4] / "pact"
    if not (root / "runtime" / "engine.py").is_file():
        raise PactUnavailableError(
            f"pact runtime not found at {root} (set PACT_ROOT to override)"
        )
    return root


@lru_cache(maxsize=1)
def _load_execute() -> Callable[[dict[str, Any]], dict[str, Any]]:
    root = _resolve_pact_root()
    root_str = str(root)
    if root_str not in sys.path:
        sys.path.insert(0, root_str)
    try:
        from runtime.engine import execute_slice_07  # type: ignore[import-not-found]
    except Exception as exc:  # pragma: no cover - import hardening surface
        raise PactUnavailableError(f"cannot import pact runtime: {exc}") from exc
    return execute_slice_07


def verify_packet(request: dict[str, Any]) -> dict[str, Any]:
    """Run a pact verification request and return its result dict.

    The result has ``ok`` (bool), ``packet`` and ``receipt`` (both echo the
    bundle handle when connectivity fields were supplied).
    """
    execute = _load_execute()
    return execute(request)
