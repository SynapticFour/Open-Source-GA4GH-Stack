from __future__ import annotations

from pathlib import Path

import click
import questionary
import yaml
from rich.console import Console

from community_stack.config import StackConfig


def run_init_wizard() -> None:
    dest = Path.cwd() / "stack.yml"

    lab_name = questionary.text("Lab name:", default="Community Stack Lab").ask()
    if lab_name is None:
        raise click.Abort()
    contact_raw = questionary.text("Contact email or URL:").ask()
    contact = (contact_raw or "") if contact_raw is not None else ""

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

    host_default = "localhost"
    host_raw = questionary.text("Public host for redirects / Caddy:", default=host_default).ask()
    if host_raw is None:
        raise click.Abort()
    host = host_raw or host_default
    tls_raw = questionary.confirm("Terminate TLS at Caddy?", default=False).ask()
    if tls_raw is None:
        raise click.Abort()
    tls = bool(tls_raw)

    ls_block = None
    kc_block = None
    if auth == "ls-login":
        cid_r = questionary.text("LS Login client_id:").ask()
        csec_r = questionary.password("LS Login client_secret:").ask()
        if cid_r is None or csec_r is None:
            raise click.Abort()
        cid = cid_r or "replace-me"
        csec = csec_r or "replace-me"
        ls_block = {
            "client_id": cid,
            "client_secret": csec,
            "redirect_uri": f"https://{host}/oauth2/callback"
            if tls
            else f"http://{host}/oauth2/callback",
        }
    elif auth == "keycloak":
        cid_r = questionary.text("Keycloak OIDC client_id:").ask()
        csec_r = questionary.password("Keycloak OIDC client_secret:").ask()
        if cid_r is None or csec_r is None:
            raise click.Abort()
        cid = cid_r or "replace-me"
        csec = csec_r or "replace-me"
        ls_block = {
            "client_id": cid,
            "client_secret": csec,
            "redirect_uri": f"https://{host}/oauth2/callback"
            if tls
            else f"http://{host}/oauth2/callback",
        }
        default_issuer = f"http://{host}:8080/realms/master"
        iss_r = questionary.text(
            "Keycloak issuer URL (realm, no trailing slash)",
            default=default_issuer,
        ).ask()
        if iss_r is None:
            raise click.Abort()
        kc_block = {"issuer_url": (iss_r or default_issuer).rstrip("/")}

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
                "access_level": "registered",
                "dataset_name": "Primary dataset",
            },
            "wes": {"enabled": bool(wes_on), "engine": "nextflow"},
            "tes": {
                "enabled": bool(tes_on),
                "backend": "slurm",
                "slurm": {"partition": "short"},
            },
            "drs": {"enabled": bool(drs_on)},
        },
        "deploy": {"target": "compose", "host": host or host_default, "tls": bool(tls)},
    }

    StackConfig.model_validate(data)
    dest.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8")
    Console().print(f"[green]Wrote[/green] {dest}\nNächster Schritt: lab-stack generate compose")
