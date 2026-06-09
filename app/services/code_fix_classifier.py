"""Deterministic code-fix classifier — assigns the capability category (the 'what').

Deterministic-first (no model in the routing path): maps the triggering signal +
file/diff heuristics into a CodeFixClassification with provenance and a resolved
risk floor. Unclassifiable jobs fall to the generic 'unknown' kind (which must be
reclassified before PATCH per the plan). An operator-override path is provided.

The category it produces is the routing/learning cell NeuroForge keys on; the risk
floor forces a min tier for governance-critical work regardless of a cheap champion.
"""
from __future__ import annotations

from datetime import datetime, timezone

from app.domain import taxonomy as tax
from app.schemas.code_fix_classification import (
    ClassificationMethod,
    CodeFixClassification,
    RiskFloorResolution,
)

# Signal-vocabulary -> FixKind. Keys are matched as substrings of a normalized raw kind,
# longest-key-first, so 'missing_test' beats 'test'.
_KIND_RULES: dict[str, str] = {
    "trailing_whitespace": "hygiene", "missing_trailing_newline": "hygiene",
    "eof_newline": "hygiene", "whitespace": "hygiene", "hygiene": "hygiene",
    "format": "format", "indent": "format",
    "unused_import": "imports", "missing_import": "imports", "import_order": "imports", "import": "imports",
    "lint": "lint", "style": "lint",
    "typo": "typo_naming", "rename": "typo_naming", "naming": "typo_naming",
    "type_error": "type_annotation", "annotation": "type_annotation", "typing": "type_annotation",
    "mypy": "type_annotation", "type": "type_annotation",
    "signature": "signature",
    "refactor": "refactor_mechanical",
    "off_by_one": "bugfix_edgecase", "edge_case": "bugfix_edgecase", "edgecase": "bugfix_edgecase",
    "null": "bugfix_edgecase", "none_handling": "bugfix_edgecase",
    "error_handling": "error_handling", "exception": "error_handling", "try_except": "error_handling",
    "race": "concurrency", "deadlock": "concurrency", "concurrency": "concurrency",
    "async": "concurrency", "threading": "concurrency",
    "injection": "security", "xss": "security", "vuln": "security", "cve": "security",
    "secret": "security", "auth": "security", "security": "security",
    "performance": "performance", "perf": "performance", "optimization": "performance", "slow": "performance",
    "schema_migration": "data_migration", "migration": "data_migration", "alembic": "data_migration",
    "dependency": "dependency", "version_bump": "dependency", "upgrade": "dependency", "package": "dependency",
    "api_contract": "api_contract", "contract": "api_contract", "interface": "api_contract", "schema": "api_contract",
    "config": "config_build", "build": "config_build", "packaging": "config_build", "ci": "config_build",
    "failing_test": "test_fix", "test_fail": "test_fix", "test_fix": "test_fix",
    "missing_test": "test_add", "coverage": "test_add", "test_add": "test_add",
    "docstring": "docs", "documentation": "docs", "comment": "docs", "docs": "docs",
    "localization": "i18n_localization", "translation": "i18n_localization", "i18n": "i18n_localization", "l10n": "i18n_localization",
    # generic behavioral catch-alls last (shortest, most ambiguous)
    "bugfix": "bugfix_logic", "logic": "bugfix_logic", "bug": "bugfix_logic",
}

_EXT_LANG: dict[str, str] = {
    ".py": "python", ".rs": "rust", ".ts": "typescript", ".tsx": "typescript",
    ".js": "javascript", ".jsx": "javascript", ".mjs": "javascript", ".go": "go",
    ".java": "java", ".cs": "csharp", ".sql": "sql", ".sh": "shell", ".bash": "shell",
    ".yaml": "config", ".yml": "config", ".toml": "config", ".json": "config",
    ".ini": "config", ".cfg": "config", ".html": "web", ".css": "web", ".md": "markdown",
}

_RISK_PATH_MARKERS = (
    "auth", "security", "secret", "credential", "payment", "billing",
    "migration", "alembic", "crypto", "/iam", "permission",
)


def _norm(s: str) -> str:
    return (s or "").strip().lower().replace("-", "_").replace(" ", "_")


def detect_kind(raw_kind: str) -> tuple[str, bool]:
    """Map a raw signal kind -> FixKind value. Returns (kind, matched)."""
    norm = _norm(raw_kind)
    if not norm:
        return tax.FixKind.UNKNOWN.value, False
    for key in sorted(_KIND_RULES, key=len, reverse=True):
        if key in norm:
            return _KIND_RULES[key], True
    return tax.FixKind.UNKNOWN.value, False


def detect_language(file_path: str) -> str:
    name = (file_path or "").rsplit("/", 1)[-1]
    if name == "Dockerfile" or name.startswith("Dockerfile"):
        return "dockerfile"
    lower = (file_path or "").lower()
    for ext, lang in _EXT_LANG.items():
        if lower.endswith(ext):
            return lang
    return "other"


def detect_complexity(
    kind: str,
    files_changed: int | None,
    lines_changed: int | None,
) -> str:
    if files_changed is None and lines_changed is None:
        return tax.KIND_TYPICAL_COMPLEXITY.get(kind, tax.Complexity.BOUNDED.value)
    files = files_changed or 1
    lines = lines_changed or 0
    if files > 3 or lines > 200:
        return tax.Complexity.BROAD.value
    if files > 1 or lines > 40:
        return tax.Complexity.BOUNDED.value
    if lines <= 5:
        return tax.Complexity.TRIVIAL.value
    return tax.Complexity.LOCAL.value


def _path_risk(file_path: str) -> str:
    lower = (file_path or "").lower()
    if any(marker in lower for marker in _RISK_PATH_MARKERS):
        return tax.Risk.GOVERNANCE_CRITICAL.value
    return tax.Risk.STANDARD.value


class CodeFixClassifier:
    """Deterministic-first classifier. Stdlib-only; no model in the routing path."""

    REVISION = "v1"

    def classify(
        self,
        *,
        file_path: str,
        raw_kind: str = "",
        secondary_raw_kinds: tuple[str, ...] = (),
        files_changed: int | None = None,
        lines_changed: int | None = None,
        explicit_risk: str | None = None,
        context_bundle_id: str | None = None,
        now: datetime | None = None,
    ) -> CodeFixClassification:
        kind, matched = detect_kind(raw_kind)
        secondary = tuple(
            dict.fromkeys(  # dedupe, preserve order
                k for k in (detect_kind(rk)[0] for rk in secondary_raw_kinds)
                if k != kind
            )
        )
        language = detect_language(file_path)
        complexity = detect_complexity(kind, files_changed, lines_changed)

        path_risk = _path_risk(file_path)
        explicit = tax.max_risk(explicit_risk, path_risk).value
        effective_risk = tax.resolve_risk(explicit, kind, secondary)
        min_tier = tax.min_tier_for_risk(effective_risk)

        resolution = RiskFloorResolution(
            explicit_risk=explicit,
            primary_kind=kind,
            primary_kind_floor=tax.risk_floor_for_kind(kind).value,
            secondary_kind_floors=tuple((k, tax.risk_floor_for_kind(k).value) for k in secondary),
            effective_risk=effective_risk.value,
            min_tier=min_tier,
            rationale=(
                f"max(explicit={explicit}, primary[{kind}]={tax.risk_floor_for_kind(kind).value}"
                + "".join(f", secondary[{k}]={tax.risk_floor_for_kind(k).value}" for k in secondary)
                + f") -> {effective_risk.value}"
            ),
        )

        ts = (now or datetime.now(timezone.utc)).isoformat().replace("+00:00", "Z")
        return CodeFixClassification(
            family=tax.Family.CODE_FIX.value,
            kind=kind,
            secondary_kinds=secondary,
            language=language,
            complexity=complexity,
            routing_cell=tax.compose_key(tax.Family.CODE_FIX.value, kind, language, complexity),
            risk=effective_risk.value,
            min_tier=min_tier,
            risk_resolution=resolution,
            classification_method=ClassificationMethod.DETERMINISTIC_RULE.value,
            classifier_identity="forgehq.code_fix_classifier",
            classifier_revision=self.REVISION,
            confidence=0.9 if matched else 0.4,
            classification_timestamp=ts,
            taxonomy_version=tax.TAXONOMY_VERSION,
            context_bundle_id=context_bundle_id,
        )

    def operator_override(
        self,
        base: CodeFixClassification,
        *,
        kind: str,
        actor: str,
        reason: str,
        now: datetime | None = None,
    ) -> CodeFixClassification:
        """Operator reassigns the kind; recomputes cell + risk, preserving lineage."""
        effective_risk = tax.resolve_risk(base.risk_resolution.explicit_risk, kind, base.secondary_kinds)
        min_tier = tax.min_tier_for_risk(effective_risk)
        resolution = RiskFloorResolution(
            explicit_risk=base.risk_resolution.explicit_risk,
            primary_kind=kind,
            primary_kind_floor=tax.risk_floor_for_kind(kind).value,
            secondary_kind_floors=base.risk_resolution.secondary_kind_floors,
            effective_risk=effective_risk.value,
            min_tier=min_tier,
            rationale=f"operator override to kind={kind}; " + base.risk_resolution.rationale,
        )
        ts = (now or datetime.now(timezone.utc)).isoformat().replace("+00:00", "Z")
        return CodeFixClassification(
            family=base.family,
            kind=kind,
            secondary_kinds=base.secondary_kinds,
            language=base.language,
            complexity=base.complexity,
            routing_cell=tax.compose_key(base.family, kind, base.language, base.complexity),
            risk=effective_risk.value,
            min_tier=min_tier,
            risk_resolution=resolution,
            classification_method=ClassificationMethod.OPERATOR_ASSIGNED.value,
            classifier_identity=base.classifier_identity,
            classifier_revision=self.REVISION,
            confidence=1.0,
            classification_timestamp=ts,
            taxonomy_version=tax.TAXONOMY_VERSION,
            context_bundle_id=base.context_bundle_id,
            previous_classification_id=base.routing_cell,
            manual_overrides=(*base.manual_overrides, f"kind:{base.kind}->{kind}"),
            override_actor=actor,
            override_reason=reason,
        )
