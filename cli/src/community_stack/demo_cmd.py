from __future__ import annotations

import subprocess
import time
from pathlib import Path

import click
import httpx
from rich.console import Console

from community_stack.generate import run_generate_compose
from community_stack.paths import default_project_output_dir, find_assets_root

_COMPOSE_UP_TIMEOUT_S = 600.0
_COMPOSE_DOWN_TIMEOUT_S = 120.0
_MONGOIMPORT_TIMEOUT_S = 60.0


def _docker(args: list[str], *, timeout: float) -> None:
    try:
        subprocess.run(args, check=True, timeout=timeout)
    except FileNotFoundError as exc:
        raise click.ClickException("docker not found on PATH") from exc
    except subprocess.TimeoutExpired as exc:
        raise click.ClickException(f"timed out running: {' '.join(args[:6])}") from exc
    except subprocess.CalledProcessError as exc:
        raise click.ClickException(
            f"command failed (exit {exc.returncode}): {' '.join(args[:6])}"
        ) from exc


def run_demo_seed(*, project_dir: Path, compose_file: Path) -> None:
    demo_dir = project_dir / "data" / "demo"
    mapping = [
        ("datasets.json", "datasets"),
        ("cohorts.json", "cohorts"),
        ("individuals.json", "individuals"),
        ("genomicVariations.json", "genomicVariations"),
    ]
    for filename, collection in mapping:
        fp = demo_dir / filename
        if not fp.is_file():
            continue
        # Password stays inside the container env — not on the host argv.
        inner = (
            "mongoimport --authenticationDatabase admin -u root "
            '-p "$MONGO_INITDB_ROOT_PASSWORD" '
            f"--db beacon --collection {collection} --jsonArray --file /demo/{filename}"
        )
        _docker(
            [
                "docker",
                "compose",
                "-f",
                str(compose_file),
                "--project-directory",
                str(project_dir),
                "exec",
                "-T",
                "mongodb",
                "sh",
                "-c",
                inner,
            ],
            timeout=_MONGOIMPORT_TIMEOUT_S,
        )


def wait_for_beacon(url: str, timeout_s: float = 60.0) -> None:
    deadline = time.monotonic() + timeout_s
    err: Exception | None = None
    with httpx.Client(timeout=5.0) as client:
        while time.monotonic() < deadline:
            try:
                r = client.get(url)
                if r.status_code == 200:
                    return
            except httpx.HTTPError as exc:
                err = exc
            time.sleep(2.0)
    msg = f"Beacon did not become ready at {url}"
    if err is not None:
        raise click.ClickException(msg) from err
    raise click.ClickException(msg)


def _resolve_stack_yaml(project_dir: Path) -> Path | None:
    for candidate in (Path.cwd() / "stack.yml", project_dir / "stack.yml"):
        if candidate.is_file():
            return candidate
    return None


def run_demo_start() -> None:
    assets = find_assets_root()
    project_dir = default_project_output_dir(assets)
    profile = assets / "config" / "profiles" / "beacon-only.env"
    compose_path = run_generate_compose(
        assets_root=assets,
        stack_yaml=_resolve_stack_yaml(project_dir),
        profile_path=profile,
        output_dir=project_dir,
        demo_mode=True,
    )

    _docker(
        [
            "docker",
            "compose",
            "-f",
            str(compose_path),
            "--project-directory",
            str(project_dir),
            "up",
            "-d",
        ],
        timeout=_COMPOSE_UP_TIMEOUT_S,
    )

    wait_for_beacon("http://localhost:5050/ga4gh/beacon/v2/service-info")
    run_demo_seed(project_dir=project_dir, compose_file=compose_path)

    Console().print(
        "[green]Beacon v2[/green] läuft auf: "
        "http://localhost:5050/ga4gh/beacon/v2\n"
        "API-Docs (falls vom Image bereitgestellt): http://localhost:5050/docs\n"
        "Demo-Query: "
        "curl http://localhost:5050/ga4gh/beacon/v2/individuals"
    )


def _find_compose_project() -> tuple[Path, Path]:
    """Return (project_dir, compose_path) for an existing generated demo."""
    assets = find_assets_root()
    for base in (Path.cwd(), default_project_output_dir(assets)):
        compose_path = base / "docker-compose.generated.yml"
        if compose_path.is_file():
            return base, compose_path
    raise click.ClickException(
        "docker-compose.generated.yml nicht gefunden — zuerst "
        "'lab-stack demo start' ausführen."
    )


def run_demo_stop(*, volumes: bool = False) -> None:
    project_dir, compose_path = _find_compose_project()
    args = [
        "docker",
        "compose",
        "-f",
        str(compose_path),
        "--project-directory",
        str(project_dir),
        "down",
        "--remove-orphans",
    ]
    if volumes:
        args.append("-v")
    _docker(args, timeout=_COMPOSE_DOWN_TIMEOUT_S)
    if volumes:
        Console().print("[green]Demo-Stack entfernt (Volumes gelöscht).[/green]")
    else:
        Console().print("[green]Demo gestoppt (Daten behalten).[/green]")


def run_demo_seed_only() -> None:
    assets = find_assets_root()
    for base in (Path.cwd(), default_project_output_dir(assets)):
        compose_path = base / "docker-compose.generated.yml"
        if compose_path.is_file():
            run_demo_seed(project_dir=base, compose_file=compose_path)
            Console().print("[green]Demo-Daten eingespielt.[/green]")
            return
    raise click.ClickException(
        "docker-compose.generated.yml nicht gefunden — zuerst "
        "'lab-stack generate compose' oder 'lab-stack demo start' ausführen."
    )
