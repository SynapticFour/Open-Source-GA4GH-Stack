from __future__ import annotations

from pathlib import Path

import click
import pytest
import yaml

from community_stack.config import StackConfig
from community_stack.generate import GenerateContext, generate_compose, resolve_stack_config

ASSETS = Path(__file__).resolve().parents[2]


def _stack(**overrides: object) -> StackConfig:
    data: dict[str, object] = {
        "lab": {"name": "Test Lab", "contact": "a@b.org"},
        "auth": {"provider": "none"},
        "services": {
            "beacon": {"enabled": True, "access_level": "public", "dataset_name": "Demo"},
            "wes": {"enabled": False, "engine": "nextflow"},
            "tes": {"enabled": False, "backend": "local"},
            "drs": {"enabled": False},
        },
        "deploy": {"target": "compose", "host": "localhost", "tls": False},
    }
    for key, value in overrides.items():
        data[key] = value
    return StackConfig.model_validate(data)


def _ctx(
    tmp_path: Path,
    stack: StackConfig,
    *,
    profile: dict[str, str] | None = None,
    demo: bool = True,
) -> GenerateContext:
    return GenerateContext(
        assets_root=ASSETS,
        output_dir=tmp_path,
        stack=stack,
        profile=profile or {"COOKIE_SECRET": "a" * 32, "MONGO_PASSWORD": "testpw"},
        demo_skip_auth=demo,
    )


def test_funnel_compute_local(tmp_path: Path) -> None:
    stack = _stack(
        services={
            "beacon": {"enabled": False},
            "tes": {"enabled": True, "backend": "local", "slurm": {"partition": "short"}},
        }
    )
    generate_compose(_ctx(tmp_path, stack))
    text = (tmp_path / "config" / "funnel" / "funnel.conf").read_text(encoding="utf-8")
    assert "Compute: local" in text
    assert "Partition:" not in text


def test_funnel_compute_slurm(tmp_path: Path) -> None:
    stack = _stack(
        services={
            "beacon": {"enabled": False},
            "tes": {"enabled": True, "backend": "slurm", "slurm": {"partition": "gpu"}},
        }
    )
    generate_compose(_ctx(tmp_path, stack))
    text = (tmp_path / "config" / "funnel" / "funnel.conf").read_text(encoding="utf-8")
    assert "Compute: slurm" in text
    assert 'Partition: "gpu"' in text


def test_funnel_kubernetes_rejected(tmp_path: Path) -> None:
    stack = _stack(
        services={
            "beacon": {"enabled": False},
            "tes": {"enabled": True, "backend": "kubernetes"},
        }
    )
    with pytest.raises(click.ClickException, match="kubernetes"):
        generate_compose(_ctx(tmp_path, stack))


def test_wes_engine_snakemake(tmp_path: Path) -> None:
    stack = _stack(
        services={
            "beacon": {"enabled": False},
            "wes": {"enabled": True, "engine": "snakemake"},
        }
    )
    generate_compose(_ctx(tmp_path, stack))
    raw = (tmp_path / "config" / "sapporo" / "executable_workflows.json").read_text(
        encoding="utf-8"
    )
    data = yaml.safe_load(raw)
    assert data[0]["workflow_type"] == "Snakemake"
    assert data[0]["workflow_type_version"] == "7.32.0"


def test_caddy_forward_auth_when_gated(tmp_path: Path) -> None:
    stack = _stack(
        auth={"provider": "ls-login", "ls_login": {"client_id": "id", "client_secret": "s"}}
    )
    generate_compose(_ctx(tmp_path, stack, demo=False))
    caddy = (tmp_path / "config" / "caddy" / "Caddyfile").read_text(encoding="utf-8")
    assert "forward_auth oauth2-proxy:4180" in caddy
    compose = yaml.safe_load(
        (tmp_path / "docker-compose.generated.yml").read_text(encoding="utf-8")
    )
    assert "ports" not in compose["services"]["beacon"]


def test_caddy_no_forward_auth_in_demo(tmp_path: Path) -> None:
    stack = _stack(
        auth={"provider": "ls-login", "ls_login": {"client_id": "id", "client_secret": "s"}}
    )
    generate_compose(_ctx(tmp_path, stack, demo=True))
    caddy = (tmp_path / "config" / "caddy" / "Caddyfile").read_text(encoding="utf-8")
    assert "forward_auth" not in caddy
    compose = yaml.safe_load(
        (tmp_path / "docker-compose.generated.yml").read_text(encoding="utf-8")
    )
    assert "ports" in compose["services"]["beacon"]


def test_caddy_tes_handle_path(tmp_path: Path) -> None:
    stack = _stack(
        services={
            "beacon": {"enabled": True},
            "tes": {"enabled": True, "backend": "local"},
        }
    )
    generate_compose(_ctx(tmp_path, stack))
    caddy = (tmp_path / "config" / "caddy" / "Caddyfile").read_text(encoding="utf-8")
    assert "handle_path /ga4gh/tes/*" in caddy


def test_beacon_conf_uses_repr(tmp_path: Path) -> None:
    stack = _stack(
        lab={"name": 'Lab "quoted"', "contact": "a@b.org"},
        services={
            "beacon": {
                "enabled": True,
                "access_level": "public",
                "dataset_name": "cohort",
            }
        },
    )
    generate_compose(_ctx(tmp_path, stack))
    conf = (tmp_path / "config" / "beacon" / "conf.py").read_text(encoding="utf-8")
    assert "v2.1.2" in conf
    assert "Lab \"quoted\"" in conf
    assert "beacon_name =" in conf


def test_redirect_uri_honored(tmp_path: Path) -> None:
    stack = _stack(
        auth={
            "provider": "ls-login",
            "ls_login": {
                "client_id": "id",
                "client_secret": "s",
                "redirect_uri": "https://custom.example/oauth2/callback",
            },
        }
    )
    generate_compose(_ctx(tmp_path, stack, demo=False))
    cfg = (tmp_path / "config" / "oauth2-proxy" / "oauth2-proxy.cfg").read_text(encoding="utf-8")
    assert "https://custom.example/oauth2/callback" in cfg


def test_keycloak_client_not_ls_login(tmp_path: Path) -> None:
    stack = _stack(
        auth={
            "provider": "keycloak",
            "keycloak": {
                "issuer_url": "http://keycloak:8080/realms/master",
                "client_id": "kc-client",
                "client_secret": "kc-secret",
            },
        }
    )
    generate_compose(_ctx(tmp_path, stack, demo=False))
    cfg = (tmp_path / "config" / "oauth2-proxy" / "oauth2-proxy.cfg").read_text(encoding="utf-8")
    assert "kc-client" in cfg
    assert "kc-secret" in cfg


def test_ensure_demo_data_keeps_operator_files(tmp_path: Path) -> None:
    demo = tmp_path / "data" / "demo"
    demo.mkdir(parents=True)
    extra = demo / "mine.json"
    extra.write_text("[]", encoding="utf-8")
    generate_compose(_ctx(tmp_path, _stack()))
    assert extra.read_text(encoding="utf-8") == "[]"
    src_demo = ASSETS / "data" / "demo"
    if src_demo.is_dir():
        names = [p.name for p in src_demo.iterdir() if p.is_file()]
        if names:
            assert (demo / names[0]).is_file()


def test_drs_external_url(tmp_path: Path) -> None:
    stack = _stack(
        services={
            "beacon": {"enabled": False},
            "drs": {"enabled": True, "external_url": "https://drs.lab.example"},
        }
    )
    generate_compose(_ctx(tmp_path, stack))
    text = (tmp_path / "config" / "drs" / "drs.config.yml").read_text(encoding="utf-8")
    assert "https://drs.lab.example" in text


def test_resolve_stack_config_yes_without_yaml(tmp_path: Path) -> None:
    env = tmp_path / "p.env"
    env.write_text("INCLUDE_BEACON=yes\nINCLUDE_WES=on\nTLS=on\n", encoding="utf-8")
    cfg, _ = resolve_stack_config(None, env, demo_mode=False)
    assert cfg.services.beacon.enabled is True
    assert cfg.services.wes.enabled is True
    assert cfg.deploy.tls is True
