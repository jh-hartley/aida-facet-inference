#!/bin/bash

FIX_MODE=false
if [ "$1" == "--fix" ]; then
    FIX_MODE=true
fi

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

EXCLUDES_REGEX="($(IFS="|"; echo "${EXCLUDES[*]}"))"
EXCLUDES_LIST=$(IFS=","; echo "${EXCLUDES[*]}")
ISORT_SKIPS=""
for skip in "${EXCLUDES[@]}"; do
    ISORT_SKIPS="$ISORT_SKIPS --skip $skip"
done

echo "Running code quality checks..."

echo "Running black..."
if [ "$FIX_MODE" = true ]; then
    echo "Fixing black formatting..."
    black . --line-length 79
else
    black . --check --verbose --line-length 79
fi
if [ $? -ne 0 ]; then
    echo "Black check failed"
    echo "Run './scripts/check.sh --fix' to automatically fix formatting issues"
    exit 1
fi

echo "Running isort..."
if [ "$FIX_MODE" = true ]; then
    echo "Fixing import sorting..."
    isort . $ISORT_SKIPS
else
    isort . --check-only --diff $ISORT_SKIPS
fi
if [ $? -ne 0 ]; then
    echo "isort check failed"
    echo "Run './scripts/check.sh --fix' to automatically fix import sorting"
    exit 1
fi

echo "Running flake8..."
flake8 . --show-source --exclude=$EXCLUDES_LIST --max-line-length=79
if [ $? -ne 0 ]; then
    echo "flake8 check failed"
    echo "Please fix the issues shown above"
    exit 1
fi

echo "Running mypy..."
mypy src/ --show-error-codes
if [ $? -ne 0 ]; then
    echo "mypy check failed"
    echo "Please fix the type errors shown above"
    exit 1
fi

echo "Running tests..."
pytest tests/ -v
if [ $? -ne 0 ]; then
    echo "tests failed"
    echo "Please fix the failing tests shown above"
    exit 1
fi

echo "All checks passed!" 