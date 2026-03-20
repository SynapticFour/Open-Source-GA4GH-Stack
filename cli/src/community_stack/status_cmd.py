from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import httpx
from rich.console import Console
from rich.table import Table

from community_stack.config import StackConfig
from community_stack.generate import include_base_from_stack, resolve_stack_config


@dataclass(frozen=True)
class ServiceProbe:
    name: str
    url: str
    kind: str  # "ga4gh" | "ping" | "tes"


def probes_for_stack(cfg: StackConfig, profile: dict[str, str]) -> list[ServiceProbe]:
    out: list[ServiceProbe] = []
    if cfg.services.beacon.enabled:
        out.append(
            ServiceProbe(
                "Beacon v2",
                "http://localhost:5050/ga4gh/beacon/v2/service-info",
                "ga4gh",
            )
        )
    if cfg.services.wes.enabled:
        out.append(ServiceProbe("WES", "http://localhost:1122/service-info", "ga4gh"))
    if cfg.services.tes.enabled:
        out.append(ServiceProbe("TES", "http://localhost:8000/v1/tasks", "tes"))
    if cfg.services.drs.enabled:
        out.append(ServiceProbe("DRS", "http://localhost:4500/service-info", "ga4gh"))
    if include_base_from_stack(cfg, profile):
        out.append(ServiceProbe("oauth2-proxy", "http://localhost:4180/ping", "ping"))
    return out


def extract_version(kind: str, payload: Any) -> str:
    if kind == "ping":
        return "—"
    if kind == "tes" and isinstance(payload, list):
        return "1.0.0"
    if isinstance(payload, dict):
        t = payload.get("type")
        if isinstance(t, dict):
            v = t.get("version")
            if isinstance(v, str):
                return v
        alt = payload.get("version")
        if isinstance(alt, str):
            return alt
    return "—"


def run_status(*, stack_yaml: str | None, profile: str | None) -> None:
    stack_path = Path(stack_yaml) if stack_yaml else Path("stack.yml")
    profile_path = Path(profile) if profile else None
    cfg, prof = resolve_stack_config(
        stack_path if stack_path.is_file() else None,
        profile_path if profile_path and profile_path.is_file() else None,
        False,
    )

    table = Table(title="GA4GH Community Stack — health")
    table.add_column("Service")
    table.add_column("Endpoint")
    table.add_column("Status")
    table.add_column("Version")

    with httpx.Client(timeout=10.0) as client:
        for probe in probes_for_stack(cfg, prof):
            status = "✗ DOWN"
            version = "—"
            try:
                r = client.get(probe.url)
                if r.status_code == 200:
                    status = "✓ UP"
                    try:
                        version = extract_version(probe.kind, r.json())
                    except Exception:
                        version = "—"
                elif probe.kind == "tes" and r.status_code in {401, 405}:
                    # Some TES servers return auth/method quirks; treat as partially up.
                    status = "✓ UP"
                    version = "—"
            except httpx.HTTPError:
                status = "✗ DOWN"

            table.add_row(probe.name, probe.url, status, version)

    Console().print(table)
