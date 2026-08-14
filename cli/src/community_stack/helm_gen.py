from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

import click
import yaml

from community_stack.config import StackConfig
from community_stack.generate import gateway_enabled, mongo_password


def build_values(stack: StackConfig, profile: dict[str, str] | None = None) -> dict[str, Any]:
    if stack.services.tes.enabled and stack.services.tes.backend == "kubernetes":
        raise click.ClickException(
            "TES backend 'kubernetes' is not implemented; use 'local' or 'slurm'."
        )
    host = stack.deploy.host
    env = profile or {}
    return {
        "global": {"host": host, "tls": stack.deploy.tls},
        "beacon": {
            "enabled": stack.services.beacon.enabled,
            "mongo": {"password": mongo_password(env)},
        },
        "wes": {"enabled": stack.services.wes.enabled, "engine": stack.services.wes.engine},
        "tes": {
            "enabled": stack.services.tes.enabled,
            "backend": stack.services.tes.backend,
            "slurm": {"partition": stack.services.tes.slurm.partition},
        },
        "drs": {"enabled": stack.services.drs.enabled},
        "oauth2Proxy": {"enabled": stack.auth.provider != "none"},
        "caddy": {"enabled": gateway_enabled(stack), "site": host},
    }


def copy_helm_charts(assets_root: Path, dest_dir: Path) -> None:
    src = assets_root / "deploy" / "helm"
    if not (src / "Chart.yaml").is_file():
        raise click.ClickException(
            "Helm charts not found. Clone the repository or reinstall "
            "ga4gh-community-stack (wheel includes deploy/helm under _bundled)."
        )
    dest_dir.mkdir(parents=True, exist_ok=True)
    if src.resolve() == dest_dir.resolve():
        return
    shutil.copytree(
        src,
        dest_dir,
        dirs_exist_ok=True,
        ignore=shutil.ignore_patterns("values.generated.yaml"),
    )


def write_values(
    stack: StackConfig,
    dest: Path,
    profile: dict[str, str] | None = None,
) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(
        yaml.safe_dump(build_values(stack, profile), sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )
