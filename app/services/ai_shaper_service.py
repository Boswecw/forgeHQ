"""
AI shaper service for forgeHQ — the self-healing GENERATION stage, end to end.

Ties the whole AI program together:

    fetch governed precomputed context pack (context-runtime -> DataForge-Local
    context-pack store, by context_bundle_id)
      -> generate a candidate fix from it (pluggable generator: deterministic
         stub by default; the NLO ladder / NeuroForge as the real backend)
      -> pact-verify the candidate against the governed bundle (bundle-bound
         receipt — the verification evidence)
      -> shape a healing.code_fix.v1 envelope carrying that evidence
      -> publish to DataForge-Local healing-proposals (the proven apply path).

forgeHQ stays non-authoritative: it proposes; ForgeCommand's operator accepts and
applies. Fail-closed at every step — no pack, an empty/identity generation, or a
failed/ unbound verification ⇒ NO proposal is published.

Generation is intentionally pluggable so the pipeline is provable without a live
model: the default generator is a deterministic stand-in. Swapping in the real
NLO/NeuroForge generator changes only how ``new_content`` is produced.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Protocol

from app.services.code_fix_shaper import (
    CodeFixProposal,
    CodeFixShaper,
    to_healing_code_fix_envelope,
)
from app.services.pact_verification_bridge import PactVerificationBridge, grounding_ref


class ShaperError(ValueError):
    """Raised when inputs are structurally invalid — fail closed."""


class CodeFixGenerator(Protocol):
    """Produce a FULL corrected file from the governed context.

    Returns the new file content, or None for a no-op (no fix) — the shaper
    never emits an identity 'fix'.
    """

    def generate(
        self,
        *,
        repository: str,
        file_path: str,
        current_content: str,
        directive: str,
        pack: dict[str, Any],
        min_tier: str | None = None,
    ) -> str | None: ...


class DeterministicHygieneGenerator:
    """Default stand-in generator (no model): deterministic hygiene normalization.

    Stands in for the LLM so the context -> generate -> verify -> propose pipeline
    is provable end to end. Reuses the proven CodeFixShaper transforms.
    """

    def __init__(self) -> None:
        self._shaper = CodeFixShaper()

    def generate(
        self,
        *,
        repository: str,
        file_path: str,
        current_content: str,
        directive: str,
        pack: dict[str, Any],
        min_tier: str | None = None,  # ignored: deterministic transforms have no tier
    ) -> str | None:
        proposal = self._shaper.shape_all(repository, file_path, current_content)
        return proposal.new_content if proposal is not None else None


@dataclass(frozen=True)
class ShapeResult:
    proposed: bool
    reason: str
    context_bundle_id: str
    envelope: dict[str, Any] | None = None
    verdict: dict[str, Any] | None = None
    publish_response: dict[str, Any] | None = None


def _grounding_from_pack(pack: dict[str, Any], context_bundle_id: str) -> tuple[dict[str, Any], ...]:
    """Build pact grounding refs from the precomputed pack's primary + supporting."""
    refs: list[dict[str, Any]] = []
    primary = pack.get("primary") or ""
    if primary:
        refs.append(
            grounding_ref(
                f"{context_bundle_id}#primary",
                source_class="active_scene",
                excerpt=primary,
            )
        )
    for idx, item in enumerate(pack.get("supporting") or []):
        refs.append(
            grounding_ref(
                f"{context_bundle_id}#supporting/{idx}",
                source_class="adjacent_scene_summary_or_clipped_body",
                excerpt=str(item),
            )
        )
    return tuple(refs)


class AiShaperService:
    """Generate -> verify -> propose from a governed precomputed context pack."""

    def __init__(
        self,
        *,
        generator: CodeFixGenerator | None = None,
        verifier: PactVerificationBridge | None = None,
        pack_fetcher: Callable[[str], dict[str, Any]] | None = None,
        publisher: Callable[[dict[str, Any]], dict[str, Any]] | None = None,
    ) -> None:
        self._generator = generator or DeterministicHygieneGenerator()
        self._verifier = verifier or PactVerificationBridge()
        self._fetch_pack = pack_fetcher
        self._publish = publisher

    def shape(
        self,
        *,
        repository: str,
        file_path: str,
        governed: dict[str, Any],
        directive: str = "Repair the target file within the admitted context.",
        commit_sha: str = "unknown",
        severity: str = "low",
        pack: dict[str, Any] | None = None,
        publish: bool = True,
    ) -> ShapeResult:
        """Run the full generation stage for one governed target.

        ``governed`` is the lineage handle
        {task_intent_id, context_bundle_id, bundle_hash, freshness_band}.
        ``pack`` may be supplied directly; otherwise it is fetched by id.
        """
        bundle_id = governed.get("context_bundle_id")
        if not isinstance(bundle_id, str) or not bundle_id.startswith("ctxb_"):
            raise ShaperError(f"missing/invalid governed context_bundle_id: {bundle_id!r}")

        if pack is None:
            if self._fetch_pack is None:
                raise ShaperError("no pack supplied and no pack_fetcher configured")
            pack = self._fetch_pack(bundle_id)

        current_content = pack.get("primary") or ""
        if not current_content:
            return ShapeResult(False, "empty precomputed context (no primary)", bundle_id)

        # 1) generate the candidate fix from the precomputed governed context
        new_content = self._generator.generate(
            repository=repository,
            file_path=file_path,
            current_content=current_content,
            directive=directive,
            pack=pack,
        )
        if not new_content or new_content == current_content:
            return ShapeResult(False, "generator produced no change (fail-closed)", bundle_id)

        proposal = CodeFixProposal(
            repository=repository,
            file_path=file_path,
            current_content=current_content,
            new_content=new_content,
            summary=f"AI-shaped fix: {directive}",
            rule="ai_shaped",
            severity=severity,
            commit_sha=commit_sha,
        )

        # 2) pact-verify the candidate against the governed bundle (bundle-bound)
        verdict = self._verifier.verify(
            governed=governed,
            grounding_refs=_grounding_from_pack(pack, bundle_id),
            task_goal=f"Verify the proposed fix to {file_path} is grounded in the governed context.",
            instruction_block="Cite only admitted context; reject ungrounded change.",
            answer_constraints=("no speculation", "stay within admitted scope"),
        )
        if not verdict.get("ok"):
            return ShapeResult(
                False,
                f"verification failed: {verdict.get('failure_state') or 'not ok'}",
                bundle_id,
                verdict=verdict,
            )

        # 3) shape the healing envelope, carrying the verification + context evidence
        envelope = to_healing_code_fix_envelope(proposal)
        envelope["payload"]["verification"] = {
            "verifier": "pact",
            "ok": verdict.get("ok"),
            "packet_id": verdict.get("packet_id"),
            "receipt_id": verdict.get("receipt_id"),
        }
        envelope["payload"]["context"] = {
            "context_bundle_id": bundle_id,
            "context_bundle_hash": governed.get("bundle_hash"),
            "task_intent_id": governed.get("task_intent_id"),
            "served_from": "precomputed_pact_packet",
        }

        # 4) publish (proven path) — unless caller only wants the shaped envelope
        publish_response = None
        if publish:
            if self._publish is None:
                raise ShaperError("publish=True but no publisher configured")
            publish_response = self._publish(envelope)

        return ShapeResult(
            True,
            "proposed",
            bundle_id,
            envelope=envelope,
            verdict=verdict,
            publish_response=publish_response,
        )
