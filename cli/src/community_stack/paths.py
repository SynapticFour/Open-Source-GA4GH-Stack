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


def _markers_ok(root: Path) -> bool:
    return all((root / marker).is_file() for marker in _MARKERS)


def find_assets_root(start: Path | None = None) -> Path:
    """
    Root directory containing ``config/``, ``deploy/docker-compose/``, etc.

    Resolution order:

    1. Environment ``GA4GH_COMMUNITY_STACK_ROOT`` (must contain the markers)
    2. Pip wheel / sdist layout: ``community_stack/_bundled/``
    3. Walk upwards from *start* or ``cwd`` for a repository checkout
    """
    env_root = os.environ.get("GA4GH_COMMUNITY_STACK_ROOT")
    if env_root:
        p = Path(env_root).expanduser().resolve()
        miss = [m for m in _MARKERS if not (p / m).is_file()]
        if miss:
            raise FileNotFoundError(
                f"GA4GH_COMMUNITY_STACK_ROOT={p} is missing: {', '.join(miss)}"
            )
        return p

    bundled = bundled_assets_root()
    if (bundled / "deploy" / "docker-compose" / "docker-compose.base.yml").is_file():
        return bundled.resolve()

    if start is None:
        start = Path.cwd()

    for base in (start.resolve(), *start.resolve().parents):
        if _markers_ok(base):
            return base.resolve()

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


def resolve_stack_yaml(explicit: Path | None, output_dir: Path) -> Path | None:
    """Locate stack.yml: explicit path, cwd, then the project output directory."""
    if explicit is not None:
        return explicit if explicit.is_file() else None
    for candidate in (Path.cwd() / "stack.yml", output_dir / "stack.yml"):
        if candidate.is_file():
            return candidate
    return None


def resolve_profile_path(explicit: Path | None, output_dir: Path) -> Path | None:
    """Locate a .env profile: explicit ``--config``, else ``output_dir/.env`` or ``cwd/.env``."""
    if explicit is not None:
        return explicit
    for candidate in (output_dir / ".env", Path.cwd() / ".env"):
        if candidate.is_file():
            return candidate
    return None
