from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from community_stack.compose_merge import dump_compose, merge_compose_files
from community_stack.config import StackConfig, merge_profile_env
from community_stack.paths import find_repo_root


@dataclass(frozen=True)
class GenerateContext:
    repo_root: Path
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
        return profile["INCLUDE_BASE"].strip().lower() in {"1", "true", "yes", "on"}
    return gateway_enabled(cfg)


def security_levels_python(access_level: str) -> str:
    mapping = {
        "public": ["PUBLIC"],
        "registered": ["PUBLIC", "REGISTERED"],
        "controlled": ["PUBLIC", "REGISTERED", "CONTROLLED"],
    }
    levels = mapping.get(access_level, mapping["public"])
    return "[" + ", ".join(repr(x) for x in levels) + "]"


def oauth_upstream(cfg: StackConfig) -> str:
    if cfg.services.beacon.enabled:
        return "http://beacon:5050/"
    return "http://caddy:80"


def mongo_password(profile: dict[str, str]) -> str:
    return profile.get("MONGO_PASSWORD", "changeme")


def render_template(repo_root: Path, rel_template: str, out_path: Path, **ctx: object) -> None:
    tmpl_dir = repo_root / Path(rel_template).parent
    tmpl_name = Path(rel_template).name
    env = Environment(
        loader=FileSystemLoader(str(tmpl_dir)),
        autoescape=select_autoescape(enabled_extensions=()),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    tpl = env.get_template(tmpl_name)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(tpl.render(**ctx), encoding="utf-8")


def ensure_demo_data(repo_root: Path, output_dir: Path) -> None:
    src = repo_root / "data" / "demo"
    dst = output_dir / "data" / "demo"
    if src.resolve() == dst.resolve():
        return
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)


def write_dotenv(output_dir: Path, profile: dict[str, str], stack: StackConfig) -> None:
    lines = [
        f"MONGO_PASSWORD={mongo_password(profile)}",
        f"HOST={stack.deploy.host}",
    ]
    extra_keys = [
        "LS_LOGIN_CLIENT_ID",
        "LS_LOGIN_CLIENT_SECRET",
        "COOKIE_SECRET",
        "COMPOSE_PROJECT_NAME",
    ]
    for k in extra_keys:
        if k in profile:
            lines.append(f"{k}={profile[k]}")

    (output_dir / ".env").write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_compose_fragment_paths(repo_root: Path, ctx: GenerateContext) -> list[Path]:
    base = repo_root / "deploy" / "docker-compose"
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
    return paths


def generate_compose(ctx: GenerateContext) -> Path:
    repo = ctx.repo_root
    out = ctx.output_dir
    stack = ctx.stack
    profile = ctx.profile

    out.mkdir(parents=True, exist_ok=True)
    ensure_demo_data(repo, out)
    cfg_dir = out / "config"
    cfg_dir.mkdir(parents=True, exist_ok=True)

    ls = stack.auth.ls_login
    client_id = profile.get(
        "LS_LOGIN_CLIENT_ID",
        ls.client_id if ls is not None else "replace-me",
    )
    client_secret = profile.get(
        "LS_LOGIN_CLIENT_SECRET",
        ls.client_secret if ls is not None else "replace-me",
    )
    cookie_secret = profile.get(
        "COOKIE_SECRET",
        "01234567890123456789012345678901",
    )
    scheme = "https" if stack.deploy.tls else "http"
    host = stack.deploy.host
    redirect_url = f"{scheme}://{host}/oauth2/callback"

    beacon_desc = stack.services.beacon.dataset_name.replace('"', '\\"')

    if stack.services.beacon.enabled:
        render_template(
            repo,
            "config/beacon/conf.py.template",
            cfg_dir / "beacon" / "conf.py",
            beacon_id=f"org.ga4gh.community.{stack.lab.name.lower().replace(' ', '-')}",
            beacon_name=stack.lab.name,
            beacon_uri=f"{scheme}://{host}:5050",
            beacon_description=beacon_desc,
            security_levels_py=security_levels_python(stack.services.beacon.access_level),
            org_id=stack.lab.name,
            org_name=stack.lab.name,
            org_description=beacon_desc,
            org_contact=stack.lab.contact or "admin@example.org",
        )
        render_template(
            repo,
            "config/beacon/mongo/conf.env.template",
            cfg_dir / "beacon" / "mongo" / "conf.env",
            mongo_password=mongo_password(profile),
        )

    caddy_site = host
    render_template(
        repo,
        "config/caddy/Caddyfile.template",
        cfg_dir / "caddy" / "Caddyfile",
        caddy_site=caddy_site,
        caddy_health_body="GA4GH Community Stack gateway",
        beacon=stack.services.beacon.enabled,
        wes=stack.services.wes.enabled,
        tes=stack.services.tes.enabled,
        drs=stack.services.drs.enabled,
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
        oauth_upstream=oauth_upstream(stack),
    )

    if stack.services.tes.enabled:
        render_template(
            repo,
            "config/funnel/funnel.conf.template",
            cfg_dir / "funnel" / "funnel.conf",
            slurm_partition=stack.services.tes.slurm.partition,
            slurm_timelimit="4:00:00",
        )

    if stack.services.wes.enabled:
        versions = {"nextflow": "23.10.0", "snakemake": "7.32.0", "cwl": "1.2.0", "wdl": "1.0"}
        render_template(
            repo,
            "config/sapporo/executable_workflows.json.template",
            cfg_dir / "sapporo" / "executable_workflows.json",
            wes_engine_version=versions.get(stack.services.wes.engine, "23.10.0"),
        )

    if stack.services.drs.enabled:
        slug = stack.lab.name.lower().replace(" ", "-")[:32]
        render_template(
            repo,
            "config/drs/drs.config.yml.template",
            cfg_dir / "drs" / "drs.config.yml",
            service_id_slug=slug,
            contact_url=(
                f"mailto:{stack.lab.contact}"
                if stack.lab.contact
                else "mailto:admin@example.org"
            ),
        )

    fragments = build_compose_fragment_paths(repo, ctx)
    if not fragments:
        msg = "No compose fragments selected (enable at least one service or base profile)."
        raise RuntimeError(msg)

    merged = merge_compose_files(fragments)
    compose_out = out / "docker-compose.generated.yml"
    compose_out.write_text(dump_compose(merged), encoding="utf-8")

    write_dotenv(out, profile, stack)
    return compose_out


def resolve_stack_config(
    stack_yaml: Path | None,
    profile_path: Path | None,
    demo_mode: bool,
) -> tuple[StackConfig, dict[str, str]]:
    from community_stack.profile_env import parse_dotenv

    profile: dict[str, str] = parse_dotenv(profile_path) if profile_path else {}
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
                        "enabled": profile.get("INCLUDE_BEACON", "true").lower() in {"1", "true"},
                    },
                    "wes": {
                        "enabled": profile.get("INCLUDE_WES", "false").lower() in {"1", "true"},
                    },
                    "tes": {
                        "enabled": profile.get("INCLUDE_TES", "false").lower() in {"1", "true"},
                    },
                    "drs": {
                        "enabled": profile.get("INCLUDE_DRS", "false").lower() in {"1", "true"},
                    },
                },
                "deploy": {
                    "host": profile.get("HOST", "localhost"),
                    "tls": profile.get("TLS", "false").lower() in {"1", "true"},
                },
            }
        )

    if demo_mode:
        profile = {**profile, "LAB_STACK_DEMO": "1"}
    return cfg, profile


def demo_skip_auth_flag(profile: dict[str, str], explicit_demo: bool) -> bool:
    if explicit_demo:
        return True
    return profile.get("LAB_STACK_DEMO", "").strip().lower() in {"1", "true", "yes"}


def run_generate_compose(
    *,
    repo_root: Path | None,
    stack_yaml: Path | None,
    profile_path: Path | None,
    output_dir: Path | None,
    demo_mode: bool,
) -> Path:
    root = repo_root or find_repo_root()
    out = output_dir or root
    cfg, profile = resolve_stack_config(stack_yaml, profile_path, demo_mode=demo_mode)
    skip_auth = demo_skip_auth_flag(profile, explicit_demo=demo_mode)
    ctx = GenerateContext(
        repo_root=root,
        output_dir=out,
        stack=cfg,
        profile=profile,
        demo_skip_auth=skip_auth,
    )
    return generate_compose(ctx)
