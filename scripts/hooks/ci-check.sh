#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"
# Prefer venv if present
export PATH="$ROOT/.venv/bin:$PATH"
echo "ci-check: ruff"
ruff check cli/src/
echo "ci-check: mypy"
mypy cli/src/ --strict
echo "ci-check: pytest"
pytest cli/tests/ -q
echo "ci-check: OK"
