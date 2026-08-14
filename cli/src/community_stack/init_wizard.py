from __future__ import annotations

from pathlib import Path

import click
import questionary
import yaml
from rich.console import Console

from community_stack.config import StackConfig


def run_init_wizard() -> None:
    dest = Path.cwd() / "stack.yml"
    if dest.exists():
        overwrite = questionary.confirm(f"{dest} exists. Overwrite?", default=False).ask()
        if overwrite is None or not overwrite:
            raise click.Abort()

    lab_name = questionary.text("Lab name:", default="Community Stack Lab").ask()
    if lab_name is None:
        raise click.Abort()
    contact_raw = questionary.text("Contact email or URL:").ask()
    if contact_raw is None:
        raise click.Abort()
    contact = contact_raw

    auth = questionary.select(
        "Authentication provider for the gateway templates:",
        choices=[
            questionary.Choice(
                "None (local/demo — oauth2-proxy placeholders / skip in demo)",
                value="none",
            ),
            questionary.Choice("ELIXIR LS Login (OIDC)", value="ls-login"),
            questionary.Choice("Keycloak (local/dev compose fragment + OIDC)", value="keycloak"),
        ],
    ).ask()
    if auth is None:
        raise click.Abort()

    b = questionary.confirm("Enable Beacon v2?", default=True).ask()
    w = questionary.confirm("Enable WES (Sapporo)?", default=False).ask()
    t = questionary.confirm("Enable TES (Funnel)?", default=False).ask()
    d = questionary.confirm("Enable DRS (Starter Kit)?", default=False).ask()
    if None in (b, w, t, d):
        raise click.Abort()
    beacon_on, wes_on, tes_on, drs_on = b, w, t, d

    tes_backend = "local"
    tes_partition = "short"
    if tes_on:
        tes_backend = questionary.select(
            "TES compute backend:",
            choices=[
                questionary.Choice("Local Docker (Funnel Compute: local)", value="local"),
                questionary.Choice("SLURM (Funnel Compute: slurm)", value="slurm"),
            ],
            default="local",
        ).ask()
        if tes_backend is None:
            raise click.Abort()
        if tes_backend == "slurm":
            part_raw = questionary.text("SLURM partition:", default="short").ask()
            if part_raw is None:
                raise click.Abort()
            tes_partition = part_raw or "short"

    host_default = "localhost"
    host_raw = questionary.text("Public host for redirects / Caddy:", default=host_default).ask()
    if host_raw is None:
        raise click.Abort()
    host = host_raw or host_default
    tls_raw = questionary.confirm("Terminate TLS at Caddy?", default=False).ask()
    if tls_raw is None:
        raise click.Abort()
    tls = bool(tls_raw)

    target = questionary.select(
        "Default generate target (lab-stack generate with no subcommand):",
        choices=[
            questionary.Choice("Docker Compose", value="compose"),
            questionary.Choice("Helm values + charts", value="helm"),
            questionary.Choice("systemd units (SLURM login node)", value="systemd"),
        ],
        default="compose",
    ).ask()
    if target is None:
        raise click.Abort()

    ls_block = None
    kc_block = None
    scheme = "https" if tls else "http"
    derived_redirect = f"{scheme}://{host}/oauth2/callback"
    if auth == "ls-login":
        cid_r = questionary.text("LS Login client_id:").ask()
        csec_r = questionary.password("LS Login client_secret:").ask()
        if cid_r is None or csec_r is None:
            raise click.Abort()
        ls_block = {
            "client_id": cid_r or "replace-me",
            "client_secret": csec_r or "replace-me",
            "redirect_uri": derived_redirect,
        }
    elif auth == "keycloak":
        cid_r = questionary.text("Keycloak OIDC client_id:").ask()
        csec_r = questionary.password("Keycloak OIDC client_secret:").ask()
        if cid_r is None or csec_r is None:
            raise click.Abort()
        default_issuer = f"http://{host}:8080/realms/master"
        iss_r = questionary.text(
            "Keycloak issuer URL (realm, no trailing slash)",
            default=default_issuer,
        ).ask()
        if iss_r is None:
            raise click.Abort()
        kc_block = {
            "issuer_url": (iss_r or default_issuer).rstrip("/"),
            "client_id": cid_r or "replace-me",
            "client_secret": csec_r or "replace-me",
            "redirect_uri": derived_redirect,
        }

    access_level = "registered" if auth != "none" else "public"

    data = {
        "lab": {"name": lab_name or "Community Stack Lab", "contact": contact},
        "auth": {
            "provider": auth,
            "ls_login": ls_block,
            "keycloak": kc_block,
        },
        "services": {
            "beacon": {
                "enabled": bool(beacon_on),
                "access_level": access_level,
                "dataset_name": "Primary dataset",
            },
            "wes": {"enabled": bool(wes_on), "engine": "nextflow"},
            "tes": {
                "enabled": bool(tes_on),
                "backend": tes_backend,
                "slurm": {"partition": tes_partition},
            },
            "drs": {"enabled": bool(drs_on)},
        },
        "deploy": {"target": target, "host": host or host_default, "tls": bool(tls)},
    }

    StackConfig.model_validate(data)
    dest.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8")
    Console().print(f"[green]Wrote[/green] {dest}\nNächster Schritt: lab-stack generate")
