from __future__ import annotations

from pathlib import Path

import click

from community_stack import __version__
from community_stack.compare_cmd import open_comparison
from community_stack.config import StackConfig, merge_profile_env
from community_stack.demo_cmd import run_demo_seed_only, run_demo_start, run_demo_stop
from community_stack.generate import run_generate_compose
from community_stack.helm_gen import copy_helm_charts, write_values
from community_stack.init_wizard import run_init_wizard
from community_stack.paths import (
    default_project_output_dir,
    find_assets_root,
    resolve_profile_path,
    resolve_stack_yaml,
)
from community_stack.profile_env import parse_dotenv
from community_stack.status_cmd import run_status
from community_stack.systemd_gen import copy_systemd_units


@click.group()
@click.version_option(version=__version__)
def cli() -> None:
    """GA4GH Community Stack — lab-stack CLI."""


@cli.command("init")
def init_cmd() -> None:
    """Interaktiver Wizard → stack.yml."""
    run_init_wizard()


@cli.group("generate", invoke_without_command=True)
@click.pass_context
def generate_group(ctx: click.Context) -> None:
    """Render deployment artefacts (compose, helm, or systemd)."""
    if ctx.invoked_subcommand is not None:
        return
    assets = find_assets_root()
    out_base = default_project_output_dir(assets)
    stack_path = resolve_stack_yaml(None, out_base)
    if stack_path is None:
        raise click.ClickException("stack.yml not found (try `lab-stack init` or pass --stack)")
    cfg = StackConfig.from_yaml(stack_path)
    group = ctx.command
    if not isinstance(group, click.Group):
        raise click.ClickException("internal error: generate is not a Click group")
    cmd = group.get_command(ctx, cfg.deploy.target)
    if cmd is None:
        raise click.ClickException(f"unknown deploy.target {cfg.deploy.target!r}")
    ctx.invoke(cmd)


@generate_group.command("compose")
@click.option("--config", "profile", type=click.Path(path_type=Path), default=None)
@click.option("--stack", type=click.Path(path_type=Path), default=None)
@click.option("--output", type=click.Path(path_type=Path), default=None)
@click.option(
    "--demo/--no-demo",
    default=False,
    help="Demo mode: relax oauth2-proxy (skip_auth_regex).",
)
def generate_compose(
    profile: Path | None,
    stack: Path | None,
    output: Path | None,
    demo: bool,
) -> None:
    """Merge compose fragments and render config templates."""
    path = run_generate_compose(
        assets_root=None,
        stack_yaml=stack,
        profile_path=profile,
        output_dir=output,
        demo_mode=demo,
    )
    click.echo(f"Wrote {path}")


@generate_group.command("helm")
@click.option("--config", "profile", type=click.Path(path_type=Path), default=None)
@click.option("--stack", type=click.Path(path_type=Path), default=None)
@click.option(
    "--output",
    type=click.Path(path_type=Path),
    default=None,
    help="Helm chart directory (default: deploy/helm/).",
)
def generate_helm(profile: Path | None, stack: Path | None, output: Path | None) -> None:
    """Copy Helm charts and emit values.generated.yaml from stack.yml."""
    assets = find_assets_root()
    out_base = default_project_output_dir(assets)
    stack_path = resolve_stack_yaml(stack, out_base)
    if stack is not None and (stack_path is None or not stack_path.is_file()):
        raise click.ClickException(f"stack.yml not found: {stack}")
    if stack_path is None:
        raise click.ClickException(
            "stack.yml not found (try `lab-stack init` or pass --stack)",
        )
    profile_path = resolve_profile_path(profile, out_base)
    if profile is not None and (profile_path is None or not profile_path.is_file()):
        raise click.ClickException(f"profile not found: {profile}")
    env = parse_dotenv(profile_path) if profile_path is not None else {}
    cfg = merge_profile_env(StackConfig.from_yaml(stack_path), env)
    dest_dir = output or (out_base / "deploy" / "helm")
    copy_helm_charts(assets, dest_dir)
    dest = dest_dir / "values.generated.yaml"
    write_values(cfg, dest, env)
    click.echo(f"Wrote {dest}")


@generate_group.command("systemd")
@click.option(
    "--output",
    type=click.Path(path_type=Path),
    default=None,
    help="Directory for unit files.",
)
def generate_systemd(output: Path | None) -> None:
    """Copy SLURM-oriented systemd units."""
    assets = find_assets_root()
    out_base = default_project_output_dir(assets)
    dest = output or (out_base / "deploy" / "slurm" / "generated")
    copy_systemd_units(dest)
    click.echo(f"Copied systemd units to {dest}")


@cli.command("status")
@click.option("--stack", type=click.Path(path_type=Path), default=None)
@click.option("--profile", type=click.Path(path_type=Path), default=None)
def status_cmd(stack: Path | None, profile: Path | None) -> None:
    """HTTP health table for enabled services."""
    run_status(stack_yaml=stack, profile=profile)


@cli.group("demo")
def demo_group() -> None:
    """Local Beacon demo workflow."""


@demo_group.command("start")
def demo_start() -> None:
    """Generate compose, start containers, wait for Beacon, seed MongoDB."""
    run_demo_start()


@demo_group.command("stop")
@click.option("--volumes/--no-volumes", default=False, help="Also remove Docker volumes.")
def demo_stop(volumes: bool) -> None:
    """Stop the local Beacon demo stack."""
    run_demo_stop(volumes=volumes)


@demo_group.command("destroy")
def demo_destroy() -> None:
    """Stop demo stack and remove volumes."""
    run_demo_stop(volumes=True)


@demo_group.command("seed")
def demo_seed() -> None:
    """Load JSON from data/demo into MongoDB."""
    run_demo_seed_only()


@cli.command("compare")
def compare_cmd() -> None:
    """Open COMPARISON.md in $PAGER."""
    open_comparison()


if __name__ == "__main__":
    cli()
