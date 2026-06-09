"""Code-fix capability taxonomy — the "what" NeuroForge learns best-model-per-category on.

Public API over the generated, typed taxonomy (`_generated.py`, built from the
canonical `code_fix_taxonomy.v1.json`). Provides the composed routing key, the
hierarchy (for evidence pooling), and the risk-floor inheritance rule.

Runtime is stdlib-only and imports only the generated module — no JSON parsing at
runtime, no drift (the generated file is checked against the source by
tests/contract/test_taxonomy_generated.py).
"""
from __future__ import annotations

from ._generated import (
    COMPLEXITY_ORDER,
    KIND_GROUP,
    KIND_RISK_FLOOR,
    KIND_TYPICAL_COMPLEXITY,
    RISK_MIN_TIER,
    RISK_ORDER,
    TAXONOMY_VERSION,
    Complexity,
    Family,
    FixKind,
    Language,
    Risk,
)

__all__ = [
    "TAXONOMY_VERSION",
    "Family",
    "FixKind",
    "Language",
    "Complexity",
    "Risk",
    "COMPLEXITY_ORDER",
    "RISK_ORDER",
    "KIND_GROUP",
    "KIND_RISK_FLOOR",
    "KIND_TYPICAL_COMPLEXITY",
    "RISK_MIN_TIER",
    "compose_key",
    "ancestors",
    "keys_finest_to_family",
    "risk_floor_for_kind",
    "max_risk",
    "resolve_risk",
    "min_tier_for_risk",
]


def compose_key(family: str, kind: str, language: str, complexity: str) -> str:
    """The finest routing/learning cell key, e.g. 'code_fix:bugfix_logic:python:local'."""
    return f"{family}:{kind}:{language}:{complexity}"


def ancestors(key: str) -> list[str]:
    """Ancestor cells from one level coarser up to the family, e.g.
    'code_fix:bugfix_logic:python:local' -> ['code_fix:bugfix_logic:python',
    'code_fix:bugfix_logic', 'code_fix']. Drives hierarchical evidence pooling."""
    parts = key.split(":")
    return [":".join(parts[:i]) for i in range(len(parts) - 1, 0, -1)]


def keys_finest_to_family(key: str) -> list[str]:
    """The finest key plus all ancestors — record every outcome at all of these."""
    return [key, *ancestors(key)]


def risk_floor_for_kind(kind: str) -> Risk:
    """The inherent risk floor a fix kind carries (e.g. security/migration/concurrency)."""
    return Risk(KIND_RISK_FLOOR.get(kind, Risk.STANDARD.value))


def max_risk(*risks: str | None) -> Risk:
    """The strongest risk among inputs, per RISK_ORDER (the inheritance rule)."""
    best_idx = 0
    for r in risks:
        if r is None:
            continue
        try:
            best_idx = max(best_idx, RISK_ORDER.index(str(r)))
        except ValueError:
            continue
    return Risk(RISK_ORDER[best_idx])


def resolve_risk(
    explicit_risk: str | None,
    primary_kind: str,
    secondary_kinds: tuple[str, ...] = (),
) -> Risk:
    """Risk-floor inheritance: max(explicit, primary kind floor, all secondary kind floors).

    A routine-looking fix that touches a higher-risk secondary category inherits the
    stronger floor.
    """
    floors = [
        explicit_risk or Risk.STANDARD.value,
        risk_floor_for_kind(primary_kind).value,
        *(risk_floor_for_kind(k).value for k in secondary_kinds),
    ]
    return max_risk(*floors)


def min_tier_for_risk(risk: str) -> str | None:
    """The minimum NeuroForge tier this risk forces (None = let the ladder decide)."""
    return RISK_MIN_TIER.get(str(risk))
