from __future__ import annotations

from collections.abc import Mapping, MutableMapping
from pathlib import Path
from typing import Any, cast

import yaml

ComposeDict = MutableMapping[str, Any]


def deep_merge(base: ComposeDict, extra: ComposeDict) -> ComposeDict:
    result: ComposeDict = dict(base)
    for key, value in extra.items():
        if key in result and isinstance(result[key], Mapping) and isinstance(value, Mapping):
            left = cast(ComposeDict, dict(result[key]))
            right = cast(ComposeDict, dict(value))
            result[key] = deep_merge(left, right)
        else:
            result[key] = value
    return result


def load_compose(path: Path) -> ComposeDict:
    loaded: Any = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(loaded, dict):
        msg = f"Compose file must be a mapping: {path}"
        raise ValueError(msg)
    return cast(ComposeDict, loaded)


def merge_compose_files(paths: list[Path]) -> ComposeDict:
    if not paths:
        return {}
    merged = load_compose(paths[0])
    for p in paths[1:]:
        merged = deep_merge(merged, load_compose(p))
    return merged


def dump_compose(data: ComposeDict) -> str:
    return yaml.safe_dump(
        data,
        sort_keys=False,
        allow_unicode=True,
        default_flow_style=False,
        width=120,
    )


# Data-plane services whose host ports bypass Caddy / oauth2-proxy.
_GATED_SERVICES = frozenset({"beacon", "sapporo", "funnel", "drs"})


def strip_published_ports(
    data: ComposeDict,
    service_names: frozenset[str] = _GATED_SERVICES,
) -> ComposeDict:
    """Drop ``ports:`` on named services so they are reachable only on the Compose network."""
    services = data.get("services")
    if not isinstance(services, dict):
        return data
    result: ComposeDict = dict(data)
    new_services: dict[str, Any] = {}
    for name, svc in services.items():
        if name in service_names and isinstance(svc, dict) and "ports" in svc:
            updated = dict(svc)
            del updated["ports"]
            new_services[name] = updated
        else:
            new_services[name] = svc
    result["services"] = new_services
    return result
