"""neuroforge_generator — generate a code fix via NeuroForge's governed LLM ladder.

A real CodeFixGenerator backend for the AI shaper. Builds a code-fix prompt from
the governed precomputed context pack and calls NeuroForge's chat ladder
(``POST /api/v1/chat``), which routes cheapest-that-works and climbs on failure
across the 5 providers. The caller raises the tier FLOOR (``min_tier``:
FAST → STANDARD → PREMIUM) so simple fixes resolve cheap and hard ones climb to
the flagship (Opus 4.8 = PREMIUM).

The governed lineage handle (task_intent_id / context_bundle_id /
context_bundle_hash) is passed through, so NeuroForge binds the inference — and
its learning receipts — to the exact governed context the fix came from. That is
the "gets better as used" signal: which provider/model produced an accepted,
pact-verified fix for which kind of context.

Stdlib-only (urllib), same posture as the other forgeHQ drivers. Returns the FULL
corrected file (the healing contract), or None for an empty/unusable response.
"""
from __future__ import annotations

import json
import urllib.request
from dataclasses import dataclass
from typing import Any

DEFAULT_NEUROFORGE_URL = "https://neuroforge-9lxc.onrender.com"


@dataclass(frozen=True, slots=True)
class GenerationResult:
    """A generation result with the routing identity NeuroForge chose.

    `model_id` + `tier` are what the ladder selected — captured so the outcome
    feedback can teach the (model, category) champion which model produced an
    accepted, verified fix.
    """

    content: str | None
    model_id: str | None
    tier: str | None
    raw: dict[str, Any]

_SYSTEM_PROMPT = (
    "You are a precise code-fix generator. Output ONLY the complete corrected "
    "contents of the target file — no explanations, no commentary, no markdown "
    "fences, no diff. Preserve everything that should not change. Make the "
    "smallest change that resolves the issue, and stay strictly within the "
    "provided context."
)


class NeuroForgeGenerationError(RuntimeError):
    """Raised on transport / non-2xx from NeuroForge — the shaper treats it as a failed attempt."""


def _build_user_prompt(file_path: str, current_content: str, directive: str, pack: dict[str, Any]) -> str:
    supporting = pack.get("supporting") or []
    support_block = "\n\n".join(f"[context {i + 1}]\n{s}" for i, s in enumerate(supporting))
    return (
        f"Task: {directive}\n\n"
        f"Target file: {file_path}\n\n"
        f"--- CURRENT FILE CONTENT ---\n{current_content}\n--- END CURRENT FILE CONTENT ---\n\n"
        f"--- SUPPORTING CONTEXT (do not edit; for grounding only) ---\n{support_block}\n--- END SUPPORTING CONTEXT ---\n\n"
        "Return the COMPLETE corrected contents of the target file only."
    )


def _extract_full_file(content: str | None) -> str | None:
    """Pull the full corrected file from the model response.

    Strips a single surrounding markdown code fence if the model added one
    despite instructions. Returns None for empty output.
    """
    if not content or not content.strip():
        return None
    text = content.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        # drop opening fence (``` or ```lang)
        lines = lines[1:]
        # drop closing fence if present
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        text = "\n".join(lines)
    return text or None


class NeuroForgeGenerator:
    """CodeFixGenerator backed by NeuroForge's governed multi-provider chat ladder."""

    def __init__(
        self,
        *,
        base_url: str = DEFAULT_NEUROFORGE_URL,
        api_key: str | None = None,
        task_type: str = "code_fix",
        max_tokens: int = 8192,
        temperature: float = 0.0,
        timeout: float = 120.0,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key
        self._task_type = task_type
        self._max_tokens = max_tokens
        self._temperature = temperature
        self._timeout = timeout

    def build_request(
        self,
        *,
        file_path: str,
        current_content: str,
        directive: str,
        pack: dict[str, Any],
        min_tier: str | None = None,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {
            "messages": [
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": _build_user_prompt(file_path, current_content, directive, pack)},
            ],
            "task_type": self._task_type,
            "max_tokens": self._max_tokens,
            "temperature": self._temperature,
        }
        if min_tier:
            body["min_tier"] = min_tier
        # Carry the governed lineage so NeuroForge binds the inference + its
        # learning receipt to this exact context bundle.
        meta = pack.get("metadata") or {}
        for key in ("task_intent_id", "context_bundle_id", "context_bundle_hash"):
            if isinstance(meta.get(key), str) and meta[key]:
                body[key] = meta[key]
        return body

    def generate_with_metadata(
        self,
        *,
        file_path: str,
        current_content: str,
        directive: str,
        pack: dict[str, Any],
        min_tier: str | None = None,
    ) -> GenerationResult:
        """Generate and return the full file plus the model/tier the ladder chose."""
        body = self.build_request(
            file_path=file_path,
            current_content=current_content,
            directive=directive,
            pack=pack,
            min_tier=min_tier,
        )
        headers = {"Content-Type": "application/json"}
        if self._api_key:
            headers["Authorization"] = f"Bearer {self._api_key}"
        request = urllib.request.Request(
            f"{self._base_url}/api/v1/chat",
            data=json.dumps(body).encode("utf-8"),
            headers=headers,
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self._timeout) as response:
                decision = json.loads(response.read().decode("utf-8"))
        except Exception as exc:  # transport / non-2xx — a failed attempt, climb
            raise NeuroForgeGenerationError(str(exc)) from exc
        return GenerationResult(
            content=_extract_full_file(decision.get("content")),
            model_id=decision.get("model_id") or decision.get("model"),
            tier=decision.get("tier"),
            raw=decision,
        )

    def generate(
        self,
        *,
        repository: str,
        file_path: str,
        current_content: str,
        directive: str,
        pack: dict[str, Any],
        min_tier: str | None = None,
    ) -> str | None:
        return self.generate_with_metadata(
            file_path=file_path,
            current_content=current_content,
            directive=directive,
            pack=pack,
            min_tier=min_tier,
        ).content
