#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

SHOW_LIST=false
declare -a PYTEST_CMD=()

print_list() {
  cat <<'EOF'
forgeHQ regression smoke suite

1. bash doc/system/BUILD.sh
2. bash scripts/context-bundle.sh --dry-run --preset core --with-roadmap
3. pytest tests/contract/test_governance_enums.py
4. pytest tests/pipeline/test_stage_progression.py
5. pytest tests/pipeline/test_design_required_before_generation.py
6. pytest tests/pipeline/test_reviewability_requires_challenge_and_verification.py
EOF
}

discover_pytest_runner() {
  if [ -n "${PYTEST_RUNNER:-}" ]; then
    if [ -x "${PYTEST_RUNNER}" ]; then
      PYTEST_CMD=("${PYTEST_RUNNER}")
      return 0
    fi
    echo "Configured PYTEST_RUNNER is not executable: ${PYTEST_RUNNER}" >&2
    return 1
  fi

  if [ -x "${REPO_ROOT}/.venv/bin/pytest" ]; then
    PYTEST_CMD=("${REPO_ROOT}/.venv/bin/pytest")
    return 0
  fi

  if [ -x "${REPO_ROOT}/../DataForge/.venv/bin/pytest" ]; then
    PYTEST_CMD=("${REPO_ROOT}/../DataForge/.venv/bin/pytest")
    return 0
  fi

  if python3 -m pytest --version >/dev/null 2>&1; then
    PYTEST_CMD=(python3 -m pytest)
    return 0
  fi

  echo "No pytest runner found. Set PYTEST_RUNNER or provide a local pytest installation." >&2
  return 1
}

while [ $# -gt 0 ]; do
  case "$1" in
    --list)
      SHOW_LIST=true
      shift
      ;;
    *)
      echo "Unknown argument: $1" >&2
      exit 1
      ;;
  esac
done

if [ "${SHOW_LIST}" = true ]; then
  print_list
  exit 0
fi

discover_pytest_runner

echo "forgeHQ regression smoke suite"
bash "${REPO_ROOT}/doc/system/BUILD.sh"
bash "${REPO_ROOT}/scripts/context-bundle.sh" --dry-run --preset core --with-roadmap
"${PYTEST_CMD[@]}" \
  "${REPO_ROOT}/tests/contract/test_governance_enums.py" \
  "${REPO_ROOT}/tests/pipeline/test_stage_progression.py" \
  "${REPO_ROOT}/tests/pipeline/test_design_required_before_generation.py" \
  "${REPO_ROOT}/tests/pipeline/test_reviewability_requires_challenge_and_verification.py"
