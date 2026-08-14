from __future__ import annotations

import shutil
from pathlib import Path

import click

from community_stack.paths import find_assets_root


def copy_systemd_units(output_dir: Path) -> None:
    assets = find_assets_root()
    src = assets / "deploy" / "slurm"
    output_dir.mkdir(parents=True, exist_ok=True)
    for name in ("funnel.service", "sapporo.service"):
        unit = src / name
        if not unit.is_file():
            raise click.ClickException(f"systemd unit not found: {unit}")
        shutil.copyfile(unit, output_dir / name)
