#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

SHOW_CHECKLIST=false
SKIP_SUITE=false
declare -a PYTEST_CMD=()

print_checklist() {
  cat <<'EOF'
forgeHQ Mode A T0 pre-flight

- bash doc/system/BUILD.sh
- bash scripts/context-bundle.sh --list
- bash scripts/context-bundle.sh --dry-run --preset core --with-roadmap
- pytest runner exists
- repo test suite passes

Mode A boundary:
- no UI/API/database/runtime boot checks are expected yet
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

run_step() {
  local label="$1"
  shift
  local elapsed=0

  echo "[T0] ${label}"
  SECONDS=0
  "$@"
  elapsed=$SECONDS
  echo "[ok] ${label} (${elapsed}s)"
}

while [ $# -gt 0 ]; do
  case "$1" in
    --checklist)
      SHOW_CHECKLIST=true
      shift
      ;;
    --skip-suite)
      SKIP_SUITE=true
      shift
      ;;
    *)
      echo "Unknown argument: $1" >&2
      exit 1
      ;;
  esac
done

if [ "${SHOW_CHECKLIST}" = true ]; then
  print_checklist
  exit 0
fi

echo "forgeHQ Mode A T0 pre-flight"
echo "Repo maturity: contract/bootstrap repo with a Phase 1 scaffold"

run_step "documentation build parity" bash "${REPO_ROOT}/doc/system/BUILD.sh"
run_step "context bundle list" bash "${REPO_ROOT}/scripts/context-bundle.sh" --list
run_step "context bundle dry run" bash "${REPO_ROOT}/scripts/context-bundle.sh" --dry-run --preset core --with-roadmap

discover_pytest_runner
echo "[T0] pytest runner exists"
echo "[ok] pytest runner exists -> ${PYTEST_CMD[*]}"

if [ "${SKIP_SUITE}" = true ]; then
  echo "[skip] repo test suite passes (requested --skip-suite)"
  exit 0
fi

run_step "repo test suite passes" "${PYTEST_CMD[@]}" "${REPO_ROOT}/tests"
