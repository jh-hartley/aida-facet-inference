#!/bin/bash

set -euo pipefail

LINE_LENGTH=79

EXCLUDES=(
    "venv"
    ".venv"
    "env"
    ".git"
    ".github"
    "__pycache__"
    ".pytest_cache"
    ".ruff_cache"
    ".mypy_cache"
    "data"
)

log() { echo "==> $1"; }

error() {
    echo "ERROR: $1" >&2
    exit 1
}

run_check() {
    local name=$1
    local cmd=$2
    local fix_cmd=$3

    log "Running $name..."
    if ! eval "$cmd"; then
        error "$name check failed"
        if [ -n "$fix_cmd" ]; then
            echo "Run '$fix_cmd' to automatically fix the issues"
        fi
    fi
}

build_excludes() {
    # flake8 needs comma-separated list
    local excludes_list=$(IFS=","; echo "${EXCLUDES[*]}")
    
    local isort_skips=""
    for skip in "${EXCLUDES[@]}"; do
        isort_skips="$isort_skips --skip $skip"
    done
    
    echo "$excludes_list|$isort_skips"
}

main() {
    local fix_mode=false
    if [ "${1:-}" == "--fix" ]; then
        fix_mode=true
    fi

    IFS="|" read -r excludes_list isort_skips <<< "$(build_excludes)"

    log "Running code quality checks..."

    if [ "$fix_mode" = true ]; then
        log "Fixing import sorting..."
        isort . --profile black $isort_skips
        log "Fixing black formatting..."
        black . --line-length $LINE_LENGTH
    else
        run_check "black" \
            "black . --check --verbose --line-length $LINE_LENGTH" \
            "./scripts/check.sh --fix"

        run_check "isort" \
            "isort . --check-only --diff --profile black $isort_skips" \
            "./scripts/check.sh --fix"
    fi

    run_check "flake8" \
        "flake8 . --show-source --exclude=$excludes_list --max-line-length=$LINE_LENGTH" \
        ""

    run_check "mypy" \
        "mypy src/ --show-error-codes" \
        ""

    run_check "tests" \
        "pytest tests/ -v" \
        ""

    log "All checks passed! ✨"
}

main "$@" 