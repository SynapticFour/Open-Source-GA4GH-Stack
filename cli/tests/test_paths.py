from __future__ import annotations

from pathlib import Path

import pytest

from community_stack import paths

_COMPOSE = Path("deploy/docker-compose/docker-compose.base.yml")
_CONF = Path("config/beacon/conf.py.template")


def test_find_assets_root_walks_upwards(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.delenv("GA4GH_COMMUNITY_STACK_ROOT", raising=False)
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


def test_env_root_wins(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    env_repo = tmp_path / "from-env"
    (env_repo / "deploy" / "docker-compose").mkdir(parents=True)
    (env_repo / "config" / "beacon").mkdir(parents=True)
    (env_repo / _COMPOSE).write_text("x", encoding="utf-8")
    (env_repo / _CONF).write_text("x", encoding="utf-8")
    monkeypatch.setenv("GA4GH_COMMUNITY_STACK_ROOT", str(env_repo))
    other = tmp_path / "other"
    other.mkdir()
    monkeypatch.chdir(other)
    assert paths.find_assets_root().resolve() == env_repo.resolve()


def test_env_root_invalid_raises(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("GA4GH_COMMUNITY_STACK_ROOT", str(tmp_path / "missing"))
    with pytest.raises(FileNotFoundError, match="GA4GH_COMMUNITY_STACK_ROOT"):
        paths.find_assets_root()
