#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"
# Prefer venv if present
export PATH="$ROOT/.venv/bin:$PATH"
PY=(python3)
if [[ -x "$ROOT/.venv/bin/python" ]]; then
    PY=("$ROOT/.venv/bin/python")
fi
echo "ci-check: ruff"
"${PY[@]}" -m ruff check cli/src/ cli/tests/
echo "ci-check: mypy"
"${PY[@]}" -m mypy cli/src/ --strict
echo "ci-check: pytest"
"${PY[@]}" -m pytest cli/tests/ -q
echo "ci-check: OK"
