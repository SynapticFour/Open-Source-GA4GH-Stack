from __future__ import annotations

import os
from pathlib import Path

# Markers for a full repository checkout (not the pip wheel bundle layout).
_MARKERS = (
    "deploy/docker-compose/docker-compose.base.yml",
    "config/beacon/conf.py.template",
)


def package_root() -> Path:
    """Directory containing the installed ``community_stack`` package."""
    return Path(__file__).resolve().parent


def bundled_assets_root() -> Path:
    """Directory inside the wheel where templates & compose fragments are shipped."""
    return package_root() / "_bundled"


def find_assets_root(start: Path | None = None) -> Path:
    """
    Root directory containing ``config/``, ``deploy/docker-compose/``, etc.

    Resolution order:

    1. Pip wheel / sdist layout: ``community_stack/_bundled/``
    2. Walk upwards from *start* or ``cwd`` for a repository checkout
    3. Environment ``GA4GH_COMMUNITY_STACK_ROOT``
    """
    bundled = bundled_assets_root()
    if (bundled / "deploy" / "docker-compose" / "docker-compose.base.yml").is_file():
        return bundled.resolve()

    if start is None:
        start = Path.cwd()

    for base in (start.resolve(), *start.resolve().parents):
        ok = True
        for marker in _MARKERS:
            if not (base / marker).is_file():
                ok = False
                break
        if ok:
            return base.resolve()

    env_root = os.environ.get("GA4GH_COMMUNITY_STACK_ROOT")
    if env_root:
        p = Path(env_root).resolve()
        if p.is_dir():
            miss = [m for m in _MARKERS if not (p / m).is_file()]
            if not miss:
                return p

    raise FileNotFoundError(
        "GA4GH Community Stack assets not found. "
        "Install the `ga4gh-community-stack` package (includes bundled templates), "
        "clone the repository, or set GA4GH_COMMUNITY_STACK_ROOT to a checkout."
    )


def default_project_output_dir(assets_root: Path) -> Path:
    """
    Where to write ``docker-compose.generated.yml`` and ``config/`` by default.

    * **Wheel install** (assets under ``_bundled``): current working directory.
    * **Repository checkout**: repository root (same as *assets_root*).
    """
    if assets_root.resolve() == bundled_assets_root().resolve():
        return Path.cwd().resolve()
    return assets_root.resolve()


def comparison_markdown_path() -> Path:
    root = find_assets_root()
    path = root / "COMPARISON.md"
    if path.is_file():
        return path
    raise FileNotFoundError(f"COMPARISON.md not found under {root}")


def find_repo_root(start: Path | None = None) -> Path:
    """Backward-compatible alias for :func:`find_assets_root`."""
    return find_assets_root(start=start)
