"""Tests for the deterministic code-fix classifier (the 'what' + risk floor)."""
from app.domain import taxonomy as tax
from app.schemas.code_fix_classification import ClassificationMethod
from app.services.code_fix_classifier import (
    CodeFixClassifier,
    detect_complexity,
    detect_kind,
    detect_language,
)


def test_kind_mapping_specific_beats_generic():
    assert detect_kind("trailing_whitespace") == ("hygiene", True)
    assert detect_kind("missing_test") == ("test_add", True)
    assert detect_kind("failing_test") == ("test_fix", True)
    assert detect_kind("CVE-2025-1234 injection") == ("security", True)
    assert detect_kind("race condition") == ("concurrency", True)
    assert detect_kind("just a bug") == ("bugfix_logic", True)
    assert detect_kind("") == ("unknown", False)
    assert detect_kind("something we don't know") == ("unknown", False)


def test_language_detection():
    assert detect_language("app/x.py") == "python"
    assert detect_language("src/main.rs") == "rust"
    assert detect_language("web/app.tsx") == "typescript"
    assert detect_language("Dockerfile") == "dockerfile"
    assert detect_language("k8s/values.yaml") == "config"
    assert detect_language("bin/run") == "other"


def test_complexity_from_diff_stats():
    assert detect_complexity("bugfix_logic", 5, 10) == "broad"
    assert detect_complexity("bugfix_logic", 2, 10) == "bounded"
    assert detect_complexity("bugfix_logic", 1, 3) == "trivial"
    assert detect_complexity("bugfix_logic", 1, 20) == "local"
    # no stats -> kind's typical complexity
    assert detect_complexity("data_migration", None, None) == "broad"
    assert detect_complexity("hygiene", None, None) == "trivial"


def test_classify_hygiene_is_cheap_standard():
    c = CodeFixClassifier().classify(file_path="app/services/x.py", raw_kind="trailing_whitespace")
    assert c.kind == "hygiene"
    assert c.language == "python"
    assert c.routing_cell == "code_fix:hygiene:python:trivial"
    assert c.risk == "standard"
    assert c.min_tier is None
    assert c.classification_method == ClassificationMethod.DETERMINISTIC_RULE.value
    assert c.confidence == 0.9
    assert c.taxonomy_version == tax.TAXONOMY_VERSION


def test_classify_security_kind_forces_premium_floor():
    c = CodeFixClassifier().classify(file_path="app/util/parse.py", raw_kind="sql injection")
    assert c.kind == "security"
    assert c.risk == "governance_critical"
    assert c.min_tier == "PREMIUM"


def test_path_elevates_risk_even_for_benign_kind():
    # a 'hygiene' fix under an auth/ path inherits the governance-critical floor
    c = CodeFixClassifier().classify(file_path="app/auth/session.py", raw_kind="trailing_whitespace")
    assert c.kind == "hygiene"
    assert c.risk == "governance_critical"
    assert c.min_tier == "PREMIUM"
    assert c.risk_resolution.explicit_risk == "governance_critical"


def test_secondary_kind_inherits_floor():
    c = CodeFixClassifier().classify(
        file_path="app/svc.py",
        raw_kind="bugfix",
        secondary_raw_kinds=("touches schema migration",),
    )
    assert c.kind == "bugfix_logic"
    assert "data_migration" in c.secondary_kinds
    assert c.risk == "governance_critical"  # inherited from the migration secondary
    assert c.min_tier == "PREMIUM"


def test_unknown_kind_low_confidence():
    c = CodeFixClassifier().classify(file_path="app/x.py", raw_kind="???")
    assert c.kind == "unknown"
    assert c.confidence == 0.4
    assert c.routing_cell.startswith("code_fix:unknown:python:")


def test_operator_override_recomputes_and_keeps_lineage():
    clf = CodeFixClassifier()
    base = clf.classify(file_path="app/x.py", raw_kind="???")
    over = clf.operator_override(base, kind="security", actor="charlie", reason="it's an authz bug")
    assert over.kind == "security"
    assert over.risk == "governance_critical"
    assert over.min_tier == "PREMIUM"
    assert over.classification_method == ClassificationMethod.OPERATOR_ASSIGNED.value
    assert over.confidence == 1.0
    assert over.override_actor == "charlie"
    assert over.manual_overrides and "unknown->security" in over.manual_overrides[-1]
