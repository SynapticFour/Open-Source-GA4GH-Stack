from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from community_stack.config import StackConfig


def build_values(stack: StackConfig) -> dict[str, Any]:
    host = stack.deploy.host
    gateway = stack.auth.provider != "none" or sum(
        [
            stack.services.beacon.enabled,
            stack.services.wes.enabled,
            stack.services.tes.enabled,
            stack.services.drs.enabled,
        ]
    ) > 1
    return {
        "global": {"host": host, "tls": stack.deploy.tls},
        "beacon": {
            "enabled": stack.services.beacon.enabled,
            "mongo": {"password": "changeme"},
        },
        "wes": {"enabled": stack.services.wes.enabled, "engine": stack.services.wes.engine},
        "tes": {
            "enabled": stack.services.tes.enabled,
            "backend": stack.services.tes.backend,
            "slurm": {"partition": stack.services.tes.slurm.partition},
        },
        "drs": {"enabled": stack.services.drs.enabled},
        "oauth2Proxy": {"enabled": stack.auth.provider != "none"},
        "caddy": {"enabled": gateway},
    }


def write_values(stack: StackConfig, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(
        yaml.safe_dump(build_values(stack), sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )
