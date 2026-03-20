from __future__ import annotations

from pathlib import Path

import pytest

from community_stack import paths

_COMPOSE = Path("deploy/docker-compose/docker-compose.base.yml")
_CONF = Path("config/beacon/conf.py.template")


def test_find_assets_root_walks_upwards(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    repo = tmp_path / "proj"
    (repo / "deploy" / "docker-compose").mkdir(parents=True)
    (repo / "config" / "beacon").mkdir(parents=True)
    (repo / _COMPOSE).write_text("x", encoding="utf-8")
    (repo / _CONF).write_text("x", encoding="utf-8")

    sub = repo / "deep" / "nest"
    sub.mkdir(parents=True)
    monkeypatch.chdir(sub)

    assert paths.find_assets_root().resolve() == repo.resolve()


def test_default_project_output_bundled_vs_checkout(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    repo = tmp_path / "r"
    (repo / "deploy" / "docker-compose").mkdir(parents=True)
    (repo / "config" / "beacon").mkdir(parents=True)
    (repo / _COMPOSE).write_text("x", encoding="utf-8")
    (repo / _CONF).write_text("x", encoding="utf-8")

    assert paths.default_project_output_dir(repo) == repo.resolve()

    sim = tmp_path / "sim-bundled"
    (sim / "deploy" / "docker-compose").mkdir(parents=True)
    (sim / _COMPOSE).write_text("y", encoding="utf-8")
    monkeypatch.setattr(paths, "bundled_assets_root", lambda: sim)

    cwd = tmp_path / "cwd"
    cwd.mkdir()
    monkeypatch.chdir(cwd)
    assert paths.default_project_output_dir(sim.resolve()) == cwd.resolve()
