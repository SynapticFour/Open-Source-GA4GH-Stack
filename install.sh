#!/bin/sh
set -e

# GA4GH Community Stack — local clone installer for the lab-stack CLI.
# The package is not on PyPI. This script does not pip-install a registry name.

echo "GA4GH Community Stack installer"

ROOT="$(CDPATH= cd -- "$(dirname "$0")" && pwd)"
if [ ! -f "$ROOT/cli/pyproject.toml" ]; then
    echo "Run this script from a clone of SynapticFour/Open-Source-GA4GH-Stack."
    exit 1
fi

if ! command -v python3 >/dev/null 2>&1; then
    echo "python3 nicht gefunden. Bitte Python 3.11+ installieren."
    exit 1
fi

pyver=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>/dev/null || echo "0.0")
major=$(echo "$pyver" | cut -d. -f1)
minor=$(echo "$pyver" | cut -d. -f2)
if [ "$major" -lt 3 ] || { [ "$major" -eq 3 ] && [ "$minor" -lt 11 ]; }; then
    echo "Python 3.11+ erforderlich (gefunden: $pyver)."
    exit 1
fi

if command -v pip3 >/dev/null 2>&1; then
    pip3 install --user -e "$ROOT/cli"
elif command -v pip >/dev/null 2>&1; then
    pip install --user -e "$ROOT/cli"
else
    echo "pip nicht gefunden. Bitte Python 3.11+ mit pip installieren."
    exit 1
fi

echo ""
echo "lab-stack installed from this clone (not PyPI)."
echo "Lege ein Projektverzeichnis an, z. B.: mkdir ~/ga4gh-lab && cd ~/ga4gh-lab"
echo "Starte mit: lab-stack init && lab-stack generate compose"
echo "Repo & Docs: https://github.com/SynapticFour/Open-Source-GA4GH-Stack"
