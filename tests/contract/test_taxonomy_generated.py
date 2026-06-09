"""Drift guard + helpers for the code-fix taxonomy.

The generated module must always match what the canonical JSON would regenerate —
this is the anti-drift contract the plan reviews required. Also covers the public
helpers (composed key, hierarchy, risk-floor inheritance).
"""
from pathlib import Path

from app.domain import taxonomy as tax
from app.domain.taxonomy import generate


def test_generated_module_matches_canonical_source():
    """If this fails: run `python -m app.domain.taxonomy.generate` and commit."""
    committed = Path(generate.TARGET).read_text(encoding="utf-8")
    regenerated = generate.generate()
    assert committed == regenerated, (
        "taxonomy _generated.py is stale vs code_fix_taxonomy.v1.json — regenerate it"
    )


def test_enums_present_and_versioned():
    assert tax.TAXONOMY_VERSION == "code-fix-taxonomy.v1"
    assert tax.Family.CODE_FIX == "code_fix"
    assert tax.FixKind.BUGFIX_LOGIC == "bugfix_logic"
    assert tax.Language.PYTHON == "python"
    assert tax.Complexity.LOCAL == "local"
    assert tax.Risk.GOVERNANCE_CRITICAL == "governance_critical"


def test_compose_key_and_hierarchy():
    key = tax.compose_key("code_fix", "bugfix_logic", "python", "local")
    assert key == "code_fix:bugfix_logic:python:local"
    assert tax.ancestors(key) == [
        "code_fix:bugfix_logic:python",
        "code_fix:bugfix_logic",
        "code_fix",
    ]
    assert tax.keys_finest_to_family(key) == [
        "code_fix:bugfix_logic:python:local",
        "code_fix:bugfix_logic:python",
        "code_fix:bugfix_logic",
        "code_fix",
    ]


def test_risk_floor_per_kind():
    assert tax.risk_floor_for_kind("security") == tax.Risk.GOVERNANCE_CRITICAL
    assert tax.risk_floor_for_kind("data_migration") == tax.Risk.GOVERNANCE_CRITICAL
    assert tax.risk_floor_for_kind("concurrency") == tax.Risk.GOVERNANCE_CRITICAL
    assert tax.risk_floor_for_kind("hygiene") == tax.Risk.STANDARD


def test_risk_inheritance_max_rule():
    # routine-looking bugfix that also touches a security-class secondary inherits the floor
    assert tax.resolve_risk(None, "bugfix_logic", ("security",)) == tax.Risk.GOVERNANCE_CRITICAL
    # explicit governance_critical wins even with benign kinds
    assert tax.resolve_risk("governance_critical", "hygiene") == tax.Risk.GOVERNANCE_CRITICAL
    # all-benign stays standard
    assert tax.resolve_risk(None, "hygiene", ("docs",)) == tax.Risk.STANDARD


def test_min_tier_floor_for_risk():
    assert tax.min_tier_for_risk(tax.Risk.GOVERNANCE_CRITICAL) == "PREMIUM"
    assert tax.min_tier_for_risk(tax.Risk.STANDARD) is None
