from pathlib import Path
import subprocess


REPO_ROOT = Path(__file__).resolve().parents[2]
QA_DIR = REPO_ROOT / "docs" / "qa"


def test_required_qa_protocol_foundation_surfaces_exist():
    required_paths = [
        REPO_ROOT / "FORGEHQ_COMPREHENSIVE_TEST_PLAN.md",
        QA_DIR / "README.md",
        QA_DIR / "FORGEHQ_MODE_A_T0_CHECKLIST.md",
        QA_DIR / "FORGEHQ_QA_FINDINGS_LOG_TEMPLATE.md",
        QA_DIR / "FORGEHQ_QA_RUN_REPORT_TEMPLATE.md",
        QA_DIR / "FORGEHQ_TIER_APPLICABILITY_MATRIX.md",
        REPO_ROOT / "scripts" / "qa-mode-a-preflight.sh",
        REPO_ROOT / "scripts" / "qa-regression-smoke.sh",
    ]

    for path in required_paths:
        assert path.exists(), f"missing QA foundation surface: {path}"


def test_comprehensive_test_plan_declares_current_repo_maturity_and_surface_mapping():
    plan_text = (REPO_ROOT / "FORGEHQ_COMPREHENSIVE_TEST_PLAN.md").read_text()

    assert "contract/bootstrap repo with a Phase 1 scaffold" in plan_text
    assert "not a live shaping service" in plan_text

    for expected_surface in (
        "docs/architecture/forgehq-system-role.md",
        "docs/contracts/reviewability-contract.md",
        "app/domain/artifacts/enums.py",
        "app/domain/pipeline/enums.py",
        "app/domain/reviewability/enums.py",
        "app/domain/workers/enums.py",
        "app/schemas/",
        "app/orchestration/stage_router.py",
        "app/orchestration/forgehq_orchestrator.py",
        "doc/system/_index.md",
        "SYSTEM.md",
        "scripts/context-bundle.sh",
        "Browser UI",
        "HTTP routes",
        "SQL migrations",
    ):
        assert expected_surface in plan_text


def test_tier_applicability_matrix_matches_current_repo_truth():
    matrix_text = (QA_DIR / "FORGEHQ_TIER_APPLICABILITY_MATRIX.md").read_text()

    expected_phrases = (
        "T0 | Applicable now",
        "T1 | Applicable now",
        "T2 | Not applicable until UI exists",
        "T3 | Not applicable until API exists",
        "T4 | Not applicable until live runtime and multi-module flows exist",
        "T5 | Not applicable until live runtime and multi-module flows exist",
        "T6 | Limited applicability now",
        "T7 | Not applicable until packaging/release targets exist",
        "T8 | Not applicable until UI exists",
    )

    for phrase in expected_phrases:
        assert phrase in matrix_text


def test_mode_a_preflight_and_smoke_scripts_expose_required_steps():
    preflight = subprocess.run(
        ["bash", "scripts/qa-mode-a-preflight.sh", "--checklist"],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    smoke = subprocess.run(
        ["bash", "scripts/qa-regression-smoke.sh", "--list"],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    for expected_line in (
        "forgeHQ Mode A T0 pre-flight",
        "bash doc/system/BUILD.sh",
        "bash scripts/context-bundle.sh --list",
        "bash scripts/context-bundle.sh --dry-run --preset core --with-roadmap",
        "pytest runner exists",
        "repo test suite passes",
    ):
        assert expected_line in preflight.stdout

    for expected_line in (
        "forgeHQ regression smoke suite",
        "bash doc/system/BUILD.sh",
        "bash scripts/context-bundle.sh --dry-run --preset core --with-roadmap",
        "tests/contract/test_governance_enums.py",
        "tests/pipeline/test_stage_progression.py",
        "tests/pipeline/test_design_required_before_generation.py",
        "tests/pipeline/test_reviewability_requires_challenge_and_verification.py",
    ):
        assert expected_line in smoke.stdout


def test_findings_and_run_report_templates_capture_bugcheck_style_metadata():
    findings_template = (QA_DIR / "FORGEHQ_QA_FINDINGS_LOG_TEMPLATE.md").read_text()
    run_report_template = (QA_DIR / "FORGEHQ_QA_RUN_REPORT_TEMPLATE.md").read_text()

    assert "Severity" in findings_template
    assert "FORGEHQ-T0-001" in findings_template
    assert "Repo maturity" in run_report_template
    assert "Commands Executed" in run_report_template
    assert "Gate Decision" in run_report_template
