"""Generate the typed Python taxonomy module from the canonical JSON source.

One canonical, language-neutral source (`code_fix_taxonomy.v1.json`) generates the
typed downstream artifact (`_generated.py`) — so the taxonomy never drifts across
hand-maintained copies (the contract-drift risk the plan reviews flagged). This is
the Python generator; Rust/TS generators read the same JSON when a consumer exists.

Run:   python -m app.domain.taxonomy.generate
Check: tests/contract/test_taxonomy_generated.py regenerates in-memory and asserts
       the committed `_generated.py` matches (drift guard). Stdlib-only.
"""
from __future__ import annotations

import json
from pathlib import Path

_HERE = Path(__file__).resolve().parent
SOURCE = _HERE / "code_fix_taxonomy.v1.json"
TARGET = _HERE / "_generated.py"


def _enum_member(value: str) -> str:
    return value.upper()


def render(spec: dict) -> str:
    families = list(spec["families"])
    kinds = dict(spec["kinds"])
    languages = list(spec["languages"])
    complexity = list(spec["complexity_levels"])
    risk_levels = list(spec["risk_levels"])
    risk_min_tier = dict(spec["risk_min_tier"])

    lines: list[str] = []
    w = lines.append
    w('"""GENERATED from code_fix_taxonomy.v1.json — DO NOT EDIT.')
    w("")
    w("Regenerate with: python -m app.domain.taxonomy.generate")
    w('Edits belong in the canonical JSON source, then regenerate.')
    w('"""')
    w("from __future__ import annotations")
    w("")
    w("from enum import StrEnum")
    w("from types import MappingProxyType")
    w("from typing import Final, Mapping")
    w("")
    w(f'TAXONOMY_VERSION: Final[str] = {spec["version"]!r}')
    w("")

    def render_enum(name: str, values: list[str]) -> None:
        w(f"class {name}(StrEnum):")
        for v in values:
            w(f"    {_enum_member(v)} = {v!r}")
        w("")
        w("")

    render_enum("Family", families)
    render_enum("FixKind", list(kinds.keys()))
    render_enum("Language", languages)
    render_enum("Complexity", complexity)
    render_enum("Risk", risk_levels)

    # Ordered tuples (hierarchy / comparisons rely on order)
    w(f"COMPLEXITY_ORDER: Final[tuple[str, ...]] = {tuple(complexity)!r}")
    w(f"RISK_ORDER: Final[tuple[str, ...]] = {tuple(risk_levels)!r}")
    w("")

    # Per-kind tables
    kind_group = {k: v["group"] for k, v in kinds.items()}
    kind_risk_floor = {k: v["risk_floor"] for k, v in kinds.items()}
    kind_typical_complexity = {k: v["typical_complexity"] for k, v in kinds.items()}
    w(f"KIND_GROUP: Final[Mapping[str, str]] = MappingProxyType({kind_group!r})")
    w(f"KIND_RISK_FLOOR: Final[Mapping[str, str]] = MappingProxyType({kind_risk_floor!r})")
    w(
        "KIND_TYPICAL_COMPLEXITY: Final[Mapping[str, str]] = "
        f"MappingProxyType({kind_typical_complexity!r})"
    )
    w(f"RISK_MIN_TIER: Final[Mapping[str, str | None]] = MappingProxyType({risk_min_tier!r})")
    w("")
    return "\n".join(lines) + "\n"


def generate() -> str:
    spec = json.loads(SOURCE.read_text(encoding="utf-8"))
    return render(spec)


def main() -> None:
    TARGET.write_text(generate(), encoding="utf-8")
    print(f"wrote {TARGET}")


if __name__ == "__main__":
    main()
