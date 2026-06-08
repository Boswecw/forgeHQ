"""
Signal source authority classification for forgeHQ.

Source refs use URI-scheme prefixes to declare their authority class:
  forgeeval://  → deterministic evidence from ForgeEval
  forgemath://  → governed mathematical authority from ForgeMath
  cloud://      → cloud advisory proposal (ForgeCommand cloud diagnostics) — weak
  signal://     → ecosystem weak signal (coverage, mutation, regression, etc.)
  anything else → UNKNOWN — always rejected at intake

forgeHQ consumes these sources but never overwrites the upstream authority
of ForgeEval or ForgeMath artifacts.
"""
from enum import StrEnum
from types import MappingProxyType
from typing import Final


class SourceAuthorityClass(StrEnum):
    DETERMINISTIC_EVIDENCE = "deterministic_evidence"
    GOVERNED_MATH = "governed_math"
    WEAK_SIGNAL = "weak_signal"
    UNKNOWN = "unknown"


class AdmissibilityDecision(StrEnum):
    ADMITTED = "admitted"
    REJECTED = "rejected"


# Scheme → authority class for all admitted ref types.
_SCHEME_TO_AUTHORITY: Final = MappingProxyType(
    {
        "forgeeval": SourceAuthorityClass.DETERMINISTIC_EVIDENCE,
        "forgemath": SourceAuthorityClass.GOVERNED_MATH,
        # Cloud advisory proposals (FC-server cloud diagnostics) are
        # non-deterministic AI recommendations -> weak (advisory) signal.
        "cloud": SourceAuthorityClass.WEAK_SIGNAL,
        "signal": SourceAuthorityClass.WEAK_SIGNAL,
    }
)


def classify_source_authority(source_ref: str) -> SourceAuthorityClass:
    """Return the authority class for a source ref based on its URI scheme."""
    if "://" not in source_ref:
        return SourceAuthorityClass.UNKNOWN
    scheme = source_ref.split("://", 1)[0].lower()
    return _SCHEME_TO_AUTHORITY.get(scheme, SourceAuthorityClass.UNKNOWN)


def is_admissible(source_ref: str) -> bool:
    """Return True if the source ref carries an admitted URI scheme."""
    return classify_source_authority(source_ref) != SourceAuthorityClass.UNKNOWN
