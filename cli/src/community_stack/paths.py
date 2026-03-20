from __future__ import annotations

import os
from pathlib import Path

MARKERS = ("deploy/docker-compose/docker-compose.base.yml", "config/beacon/conf.py.template")


def find_repo_root(start: Path | None = None) -> Path:
    """Locate the GA4GH Community Stack repository root."""
    if start is None:
        start = Path.cwd()

    for base in (start.resolve(), *start.resolve().parents):
        ok = True
        for marker in MARKERS:
            if not (base / marker).is_file():
                ok = False
                break
        if ok:
            return base

    env_root = os.environ.get("GA4GH_COMMUNITY_STACK_ROOT")
    if env_root:
        p = Path(env_root).resolve()
        if p.is_dir():
            return p

    raise FileNotFoundError(
        "Could not find GA4GH Community Stack repo root "
        "(expected deploy/docker-compose/docker-compose.base.yml). "
        "Set GA4GH_COMMUNITY_STACK_ROOT or run from the repository."
    )


def package_root() -> Path:
    """Directory containing this Python package."""
    return Path(__file__).resolve().parent
