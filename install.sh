#!/bin/sh
set -e

# GA4GH Community Stack — pip installer for the lab-stack CLI
# Usage: curl -sSL https://example/install.sh | sh   (adjust URL when published)

echo "GA4GH Community Stack installer"

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
    pip3 install --user "ga4gh-community-stack"
elif command -v pip >/dev/null 2>&1; then
    pip install --user "ga4gh-community-stack"
else
    echo "pip nicht gefunden. Bitte Python 3.11+ mit pip installieren."
    exit 1
fi

echo ""
echo "GA4GH Community Stack installiert."
echo "Starte mit: lab-stack init"
echo "Dokumentation: https://ga4gh-community-stack.synapticfour.dev"
