from __future__ import annotations

import json
import secrets
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path

import click
from jinja2 import Environment, FileSystemLoader, select_autoescape

from community_stack.compose_merge import (
    dump_compose,
    merge_compose_files,
    strip_published_ports,
)
from community_stack.config import (
    AccessLevel,
    StackConfig,
    TesBackend,
    WesEngine,
    merge_profile_env,
)
from community_stack.paths import (
    default_project_output_dir,
    find_assets_root,
    resolve_profile_path,
    resolve_stack_yaml,
)
from community_stack.profile_env import parse_bool, parse_dotenv

BEACON_API_VERSION = "v2.1.2"

WES_ENGINE_META: dict[WesEngine, tuple[str, str]] = {
    "nextflow": ("Nextflow", "23.10.0"),
    "snakemake": ("Snakemake", "7.32.0"),
    "cwl": ("CWL", "1.2.0"),
    "wdl": ("WDL", "1.0"),
}

_KNOWN_COOKIE_SECRETS = frozenset(
    {
        "01234567890123456789012345678901",
        "change-me-to-32-byte-secret-hex",
    }
)

_JINJA_ENVS: dict[str, Environment] = {}


@dataclass(frozen=True)
class GenerateContext:
    assets_root: Path
    output_dir: Path
    stack: StackConfig
    profile: dict[str, str]
    demo_skip_auth: bool


def gateway_enabled(cfg: StackConfig) -> bool:
    active = sum(
        [
            cfg.services.beacon.enabled,
            cfg.services.wes.enabled,
            cfg.services.tes.enabled,
            cfg.services.drs.enabled,
        ]
    )
    if cfg.auth.provider != "none":
        return True
    return active > 1


def include_base_from_stack(cfg: StackConfig, profile: dict[str, str]) -> bool:
    if "INCLUDE_BASE" in profile:
        return parse_bool(profile.get("INCLUDE_BASE"))
    return gateway_enabled(cfg)


def security_levels_python(access_level: AccessLevel) -> str:
    mapping: dict[AccessLevel, list[str]] = {
        "public": ["PUBLIC"],
        "registered": ["PUBLIC", "REGISTERED"],
        "controlled": ["PUBLIC", "REGISTERED", "CONTROLLED"],
    }
    levels = mapping[access_level]
    return "[" + ", ".join(repr(x) for x in levels) + "]"


def oauth_upstream(cfg: StackConfig, profile: dict[str, str]) -> str:
    """Auth-only static upstream when Caddy is the public gateway (forward_auth)."""
    if include_base_from_stack(cfg, profile):
        return "static://202"
    if cfg.services.beacon.enabled:
        return "http://beacon:5050/"
    return "http://caddy:80"


def oidc_issuer_for_stack(stack: StackConfig) -> str:
    if stack.auth.provider == "keycloak":
        kc = stack.auth.keycloak
        base = (
            kc.issuer_url if kc is not None else "http://keycloak:8080/realms/master"
        ).rstrip("/")
        return f"{base}/"
    return "https://login.elixir-czech.org/oidc/"


def redirect_url_for_stack(stack: StackConfig) -> str:
    if stack.auth.provider == "keycloak" and stack.auth.keycloak is not None:
        if stack.auth.keycloak.redirect_uri:
            return stack.auth.keycloak.redirect_uri
    if stack.auth.ls_login is not None and stack.auth.ls_login.redirect_uri:
        return stack.auth.ls_login.redirect_uri
    scheme = "https" if stack.deploy.tls else "http"
    return f"{scheme}://{stack.deploy.host}/oauth2/callback"


def oidc_client_credentials(stack: StackConfig, profile: dict[str, str]) -> tuple[str, str]:
    if stack.auth.provider == "keycloak":
        kc = stack.auth.keycloak
        client_id = (
            profile.get("OIDC_CLIENT_ID")
            or profile.get("LS_LOGIN_CLIENT_ID")
            or (kc.client_id if kc is not None else "replace-me")
        )
        client_secret = (
            profile.get("OIDC_CLIENT_SECRET")
            or profile.get("LS_LOGIN_CLIENT_SECRET")
            or (kc.client_secret if kc is not None else "replace-me")
        )
        return client_id, client_secret
    ls = stack.auth.ls_login
    client_id = profile.get(
        "LS_LOGIN_CLIENT_ID",
        ls.client_id if ls is not None else "replace-me",
    )
    client_secret = profile.get(
        "LS_LOGIN_CLIENT_SECRET",
        ls.client_secret if ls is not None else "replace-me",
    )
    return client_id, client_secret


def mongo_password(profile: dict[str, str]) -> str:
    return profile.get("MONGO_PASSWORD") or "changeme"


def _warn(message: str) -> None:
    print(message, file=sys.stderr)


def ensure_secrets(
    stack: StackConfig,
    profile: dict[str, str],
    *,
    demo_skip_auth: bool,
) -> dict[str, str]:
    """Fill COOKIE_SECRET / MONGO_PASSWORD; rotate well-known cookie secrets when auth is on."""
    out = dict(profile)
    cookie = out.get("COOKIE_SECRET", "").strip()
    auth_on = stack.auth.provider != "none" and not demo_skip_auth
    if not cookie or (auth_on and cookie in _KNOWN_COOKIE_SECRETS):
        out["COOKIE_SECRET"] = secrets.token_hex(16)
        if cookie in _KNOWN_COOKIE_SECRETS:
            _warn("Replaced well-known COOKIE_SECRET; the new value is in .env")
        elif auth_on:
            _warn("Generated COOKIE_SECRET (32 hex chars); stored in .env")
    if not out.get("MONGO_PASSWORD"):
        if auth_on:
            out["MONGO_PASSWORD"] = secrets.token_urlsafe(16)
            _warn("Generated MONGO_PASSWORD; stored in .env")
        else:
            out["MONGO_PASSWORD"] = "changeme"
    return out


def _jinja_env(tmpl_dir: Path) -> Environment:
    key = str(tmpl_dir.resolve())
    env = _JINJA_ENVS.get(key)
    if env is None:
        env = Environment(
            loader=FileSystemLoader(str(tmpl_dir)),
            autoescape=select_autoescape(enabled_extensions=()),
            trim_blocks=True,
            lstrip_blocks=True,
        )
        _JINJA_ENVS[key] = env
    return env


def render_template(assets_root: Path, rel_template: str, out_path: Path, **ctx: object) -> None:
    tmpl_dir = assets_root / Path(rel_template).parent
    tmpl_name = Path(rel_template).name
    tpl = _jinja_env(tmpl_dir).get_template(tmpl_name)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(tpl.render(**ctx), encoding="utf-8")


def ensure_demo_data(assets_root: Path, output_dir: Path) -> None:
    src = assets_root / "data" / "demo"
    dst = output_dir / "data" / "demo"
    if not src.is_dir():
        return
    if src.resolve() == dst.resolve():
        return
    dst.mkdir(parents=True, exist_ok=True)
    for item in src.iterdir():
        dest_item = dst / item.name
        if dest_item.exists():
            continue
        if item.is_dir():
            shutil.copytree(item, dest_item)
        else:
            shutil.copy2(item, dest_item)


def _dotenv_line(key: str, value: str) -> str:
    if any(ch in value for ch in ' \t#"\'\\$'):
        return f"{key}={json.dumps(value)}"
    return f"{key}={value}"


def write_dotenv(output_dir: Path, profile: dict[str, str], stack: StackConfig) -> None:
    keys = [
        "MONGO_PASSWORD",
        "HOST",
        "LS_LOGIN_CLIENT_ID",
        "LS_LOGIN_CLIENT_SECRET",
        "OIDC_CLIENT_ID",
        "OIDC_CLIENT_SECRET",
        "COOKIE_SECRET",
        "COMPOSE_PROJECT_NAME",
    ]
    lines = [
        _dotenv_line("MONGO_PASSWORD", mongo_password(profile)),
        _dotenv_line("HOST", stack.deploy.host),
    ]
    for k in keys:
        if k in {"MONGO_PASSWORD", "HOST"}:
            continue
        if k in profile:
            lines.append(_dotenv_line(k, profile[k]))
    (output_dir / ".env").write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_compose_fragment_paths(assets_root: Path, ctx: GenerateContext) -> list[Path]:
    base = assets_root / "deploy" / "docker-compose"
    paths: list[Path] = []
    if include_base_from_stack(ctx.stack, ctx.profile):
        paths.append(base / "docker-compose.base.yml")
    if ctx.stack.services.beacon.enabled:
        paths.append(base / "docker-compose.beacon.yml")
    if ctx.stack.services.wes.enabled:
        paths.append(base / "docker-compose.wes.yml")
    if ctx.stack.services.tes.enabled:
        paths.append(base / "docker-compose.tes.yml")
    if ctx.stack.services.drs.enabled:
        paths.append(base / "docker-compose.drs.yml")
    if ctx.stack.auth.provider == "keycloak":
        paths.append(base / "docker-compose.keycloak.yml")
    return paths


def _cors_urls(stack: StackConfig, beacon_uri: str) -> list[str]:
    urls = [
        beacon_uri,
        f"http://{stack.deploy.host}",
        f"https://{stack.deploy.host}",
        f"http://{stack.deploy.host}:5050",
        "http://localhost:3000",
        "http://localhost:3003",
        "http://localhost:5050",
    ]
    seen: set[str] = set()
    out: list[str] = []
    for url in urls:
        if url not in seen:
            seen.add(url)
            out.append(url)
    return out


def _funnel_compute(backend: TesBackend) -> str:
    if backend == "kubernetes":
        raise click.ClickException(
            "TES backend 'kubernetes' is not implemented; use 'local' or 'slurm'."
        )
    return backend


def generate_compose(ctx: GenerateContext) -> Path:
    repo = ctx.assets_root
    out = ctx.output_dir
    stack = ctx.stack
    profile = ensure_secrets(stack, ctx.profile, demo_skip_auth=ctx.demo_skip_auth)

    out.mkdir(parents=True, exist_ok=True)
    ensure_demo_data(repo, out)
    cfg_dir = out / "config"
    cfg_dir.mkdir(parents=True, exist_ok=True)

    client_id, client_secret = oidc_client_credentials(stack, profile)
    cookie_secret = profile["COOKIE_SECRET"]
    scheme = "https" if stack.deploy.tls else "http"
    host = stack.deploy.host
    redirect_url = redirect_url_for_stack(stack)
    use_gateway = include_base_from_stack(stack, profile)
    auth_gate = stack.auth.provider != "none" and not ctx.demo_skip_auth

    if stack.services.beacon.enabled:
        beacon_uri = f"{scheme}://{host}" if use_gateway else f"{scheme}://{host}:5050"
        slug = stack.lab.name.lower().replace(" ", "-")
        render_template(
            repo,
            "config/beacon/conf.py.template",
            cfg_dir / "beacon" / "conf.py",
            beacon_id_py=repr(f"org.ga4gh.community.{slug}"),
            beacon_name_py=repr(stack.lab.name),
            api_version_py=repr(BEACON_API_VERSION),
            beacon_uri_py=repr(beacon_uri),
            beacon_description_py=repr(stack.services.beacon.dataset_name),
            security_levels_py=security_levels_python(stack.services.beacon.access_level),
            org_id_py=repr(stack.lab.name),
            org_name_py=repr(stack.lab.name),
            org_description_py=repr(stack.services.beacon.dataset_name),
            org_contact_url_py=repr(
                f"mailto:{stack.lab.contact}" if stack.lab.contact else "mailto:admin@example.org"
            ),
            cors_urls_py=repr(_cors_urls(stack, beacon_uri)),
        )
        render_template(
            repo,
            "config/beacon/mongo/conf.env.template",
            cfg_dir / "beacon" / "mongo" / "conf.env",
            mongo_password=mongo_password(profile),
        )

    render_template(
        repo,
        "config/caddy/Caddyfile.template",
        cfg_dir / "caddy" / "Caddyfile",
        caddy_site=host,
        caddy_health_body="GA4GH Community Stack gateway",
        beacon=stack.services.beacon.enabled,
        wes=stack.services.wes.enabled,
        tes=stack.services.tes.enabled,
        drs=stack.services.drs.enabled,
        auth_enabled=auth_gate,
    )

    render_template(
        repo,
        "config/oauth2-proxy/oauth2-proxy.cfg.template",
        cfg_dir / "oauth2-proxy" / "oauth2-proxy.cfg",
        ls_login_client_id=client_id,
        ls_login_client_secret=client_secret,
        redirect_url=redirect_url,
        cookie_secret=cookie_secret,
        cookie_secure="true" if stack.deploy.tls else "false",
        demo_skip_auth=ctx.demo_skip_auth,
        oauth_upstream=oauth_upstream(stack, profile),
        oidc_issuer_url=oidc_issuer_for_stack(stack),
    )

    if stack.services.tes.enabled:
        compute = _funnel_compute(stack.services.tes.backend)
        render_template(
            repo,
            "config/funnel/funnel.conf.template",
            cfg_dir / "funnel" / "funnel.conf",
            compute=compute,
            slurm_partition=stack.services.tes.slurm.partition,
            slurm_timelimit="4:00:00",
        )

    if stack.services.wes.enabled:
        workflow_type, workflow_version = WES_ENGINE_META[stack.services.wes.engine]
        render_template(
            repo,
            "config/sapporo/executable_workflows.json.template",
            cfg_dir / "sapporo" / "executable_workflows.json",
            wes_workflow_type=workflow_type,
            wes_engine_version=workflow_version,
        )

    if stack.services.drs.enabled:
        slug = stack.lab.name.lower().replace(" ", "-")[:32]
        public = stack.services.drs.external_url or (
            f"{scheme}://{host}/ga4gh/drs" if use_gateway else f"{scheme}://{host}:4500"
        )
        render_template(
            repo,
            "config/drs/drs.config.yml.template",
            cfg_dir / "drs" / "drs.config.yml",
            service_id_slug=slug,
            drs_public_endpoint=public,
            contact_url=(
                f"mailto:{stack.lab.contact}" if stack.lab.contact else "mailto:admin@example.org"
            ),
        )

    fragments = build_compose_fragment_paths(repo, ctx)
    if not fragments:
        raise click.ClickException(
            "No compose fragments selected (enable at least one service or base profile)."
        )

    merged = merge_compose_files(fragments)
    if auth_gate:
        merged = strip_published_ports(merged)
    compose_out = out / "docker-compose.generated.yml"
    compose_out.write_text(dump_compose(merged), encoding="utf-8")

    write_dotenv(out, profile, stack)
    return compose_out


def resolve_stack_config(
    stack_yaml: Path | None,
    profile_path: Path | None,
    demo_mode: bool,
) -> tuple[StackConfig, dict[str, str]]:
    if profile_path is not None and not profile_path.is_file():
        raise click.ClickException(f"profile not found: {profile_path}")
    profile: dict[str, str] = parse_dotenv(profile_path) if profile_path else {}
    if stack_yaml is not None and not stack_yaml.is_file():
        raise click.ClickException(f"stack.yml not found: {stack_yaml}")
    if stack_yaml and stack_yaml.is_file():
        cfg = StackConfig.from_yaml(stack_yaml)
        cfg = merge_profile_env(cfg, profile)
    else:
        cfg = StackConfig.model_validate(
            {
                "lab": {"name": profile.get("LAB_NAME", "Community Stack Lab")},
                "auth": {"provider": "none"},
                "services": {
                    "beacon": {
                        "enabled": parse_bool(profile.get("INCLUDE_BEACON"), default=True),
                    },
                    "wes": {
                        "enabled": parse_bool(profile.get("INCLUDE_WES")),
                    },
                    "tes": {
                        "enabled": parse_bool(profile.get("INCLUDE_TES")),
                    },
                    "drs": {
                        "enabled": parse_bool(profile.get("INCLUDE_DRS")),
                    },
                },
                "deploy": {
                    "host": profile.get("HOST", "localhost"),
                    "tls": parse_bool(profile.get("TLS")),
                },
            }
        )

    if demo_mode:
        profile = {**profile, "LAB_STACK_DEMO": "1"}
    return cfg, profile


def demo_skip_auth_flag(profile: dict[str, str], explicit_demo: bool) -> bool:
    if explicit_demo:
        return True
    return parse_bool(profile.get("LAB_STACK_DEMO"))


def run_generate_compose(
    *,
    assets_root: Path | None,
    stack_yaml: Path | None,
    profile_path: Path | None,
    output_dir: Path | None,
    demo_mode: bool,
) -> Path:
    root = assets_root or find_assets_root()
    out = output_dir if output_dir is not None else default_project_output_dir(root)
    if stack_yaml is not None and not stack_yaml.is_file():
        raise click.ClickException(f"stack.yml not found: {stack_yaml}")
    if profile_path is not None and not profile_path.is_file():
        raise click.ClickException(f"profile not found: {profile_path}")
    resolved_stack = resolve_stack_yaml(stack_yaml, out)
    resolved_profile = resolve_profile_path(profile_path, out)
    cfg, profile = resolve_stack_config(resolved_stack, resolved_profile, demo_mode=demo_mode)
    skip_auth = demo_skip_auth_flag(profile, explicit_demo=demo_mode)
    ctx = GenerateContext(
        assets_root=root,
        output_dir=out,
        stack=cfg,
        profile=profile,
        demo_skip_auth=skip_auth,
    )
    return generate_compose(ctx)
