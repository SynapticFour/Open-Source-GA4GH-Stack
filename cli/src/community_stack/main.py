from __future__ import annotations

from pathlib import Path

import click

from community_stack.compare_cmd import open_comparison
from community_stack.demo_cmd import run_demo_seed_only, run_demo_start
from community_stack.generate import run_generate_compose
from community_stack.helm_gen import write_values
from community_stack.init_wizard import run_init_wizard
from community_stack.paths import default_project_output_dir, find_assets_root
from community_stack.status_cmd import run_status
from community_stack.systemd_gen import copy_systemd_units


@click.group()
@click.version_option()
def cli() -> None:
    """GA4GH Community Stack — lab-stack CLI."""


@cli.command("init")
def init_cmd() -> None:
    """Interaktiver Wizard → stack.yml."""
    run_init_wizard()


@cli.group("generate")
def generate_group() -> None:
    """Render deployment artefacts."""


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
@click.option("--stack", type=click.Path(path_type=Path), default=None)
@click.option(
    "--output",
    type=click.Path(path_type=Path),
    default=None,
    help="values drop-in path (default: deploy/helm/values.generated.yaml).",
)
def generate_helm(stack: Path | None, output: Path | None) -> None:
    """Emit Helm values from stack.yml."""
    from community_stack.config import StackConfig

    assets = find_assets_root()
    out_base = default_project_output_dir(assets)
    stack_path: Path | None = stack
    if stack_path is None or not stack_path.is_file():
        cwd_candidate = Path.cwd() / "stack.yml"
        stack_path = cwd_candidate if cwd_candidate.is_file() else out_base / "stack.yml"
    if not stack_path.is_file():
        raise click.ClickException(
            "stack.yml not found (try `lab-stack init` or pass --stack)",
        )
    cfg = StackConfig.from_yaml(stack_path)
    dest = output or (out_base / "deploy" / "helm" / "values.generated.yaml")
    dest.parent.mkdir(parents=True, exist_ok=True)
    write_values(cfg, dest)
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
@click.option("--stack", type=str, default=None)
@click.option("--profile", type=str, default=None)
def status_cmd(stack: str | None, profile: str | None) -> None:
    """HTTP health table for enabled services."""
    run_status(stack_yaml=stack, profile=profile)


@cli.group("demo")
def demo_group() -> None:
    """Local Beacon demo workflow."""


@demo_group.command("start")
def demo_start() -> None:
    """Generate compose, start containers, wait for Beacon, seed MongoDB."""
    run_demo_start()


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
