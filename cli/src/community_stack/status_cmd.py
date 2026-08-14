from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from json import JSONDecodeError
from pathlib import Path
from typing import Any, Literal

import click
import httpx
from rich.console import Console
from rich.table import Table

from community_stack.config import StackConfig
from community_stack.generate import include_base_from_stack, resolve_stack_config
from community_stack.paths import (
    default_project_output_dir,
    find_assets_root,
    resolve_profile_path,
    resolve_stack_yaml,
)
from community_stack.profile_env import parse_bool

ProbeKind = Literal["ga4gh", "ping", "tes"]


@dataclass(frozen=True)
class ServiceProbe:
    name: str
    url: str
    kind: ProbeKind


def probes_for_stack(cfg: StackConfig, profile: dict[str, str]) -> list[ServiceProbe]:
    scheme = "https" if cfg.deploy.tls else "http"
    host = cfg.deploy.host
    demo = parse_bool(profile.get("LAB_STACK_DEMO"))
    gated = cfg.auth.provider != "none" and not demo
    use_gateway = include_base_from_stack(cfg, profile) and gated
    origin = f"{scheme}://{host}"
    out: list[ServiceProbe] = []
    if cfg.services.beacon.enabled:
        url = (
            f"{origin}/ga4gh/beacon/v2/service-info"
            if use_gateway
            else "http://localhost:5050/ga4gh/beacon/v2/service-info"
        )
        out.append(ServiceProbe("Beacon v2", url, "ga4gh"))
    if cfg.services.wes.enabled:
        url = (
            f"{origin}/ga4gh/wes/service-info"
            if use_gateway
            else "http://localhost:1122/service-info"
        )
        out.append(ServiceProbe("WES", url, "ga4gh"))
    if cfg.services.tes.enabled:
        url = f"{origin}/ga4gh/tes/v1/tasks" if use_gateway else "http://localhost:8000/v1/tasks"
        out.append(ServiceProbe("TES", url, "tes"))
    if cfg.services.drs.enabled:
        url = (
            f"{origin}/ga4gh/drs/service-info"
            if use_gateway
            else "http://localhost:4500/service-info"
        )
        out.append(ServiceProbe("DRS", url, "ga4gh"))
    if include_base_from_stack(cfg, profile):
        out.append(ServiceProbe("oauth2-proxy", "http://localhost:4180/ping", "ping"))
    return out


def extract_version(kind: ProbeKind, payload: Any) -> str:
    if kind == "ping":
        return "—"
    if kind == "tes":
        return "—"
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


def _probe_one(probe: ServiceProbe) -> tuple[str, str]:
    status = "✗ DOWN"
    version = "—"
    try:
        with httpx.Client(timeout=10.0) as client:
            r = client.get(probe.url)
            if r.status_code == 200:
                status = "✓ UP"
                try:
                    version = extract_version(probe.kind, r.json())
                except JSONDecodeError:
                    version = "—"
            elif probe.kind == "tes" and r.status_code in {401, 405}:
                status = "✓ UP"
                version = "—"
    except httpx.HTTPError:
        status = "✗ DOWN"
    return status, version


def run_status(*, stack_yaml: Path | None, profile: Path | None) -> None:
    assets = find_assets_root()
    out_base = default_project_output_dir(assets)
    stack_path = resolve_stack_yaml(stack_yaml, out_base)
    if stack_yaml is not None and (stack_path is None or not stack_path.is_file()):
        raise click.ClickException(f"stack.yml not found: {stack_yaml}")
    profile_path = resolve_profile_path(profile, out_base)
    if profile is not None and (profile_path is None or not profile_path.is_file()):
        raise click.ClickException(f"profile not found: {profile}")
    cfg, prof = resolve_stack_config(stack_path, profile_path, False)

    table = Table(title="GA4GH Community Stack — health")
    table.add_column("Service")
    table.add_column("Endpoint")
    table.add_column("Status")
    table.add_column("Version")

    probes = probes_for_stack(cfg, prof)
    rows: list[tuple[ServiceProbe, str, str]] = []
    if probes:
        with ThreadPoolExecutor(max_workers=len(probes)) as pool:
            futs = [pool.submit(_probe_one, p) for p in probes]
            for probe, fut in zip(probes, futs, strict=True):
                status, version = fut.result()
                rows.append((probe, status, version))
    for probe, status, version in rows:
        table.add_row(probe.name, probe.url, status, version)

    Console().print(table)
