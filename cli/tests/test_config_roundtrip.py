from __future__ import annotations

from pathlib import Path

import yaml

from community_stack.config import StackConfig


def test_stack_config_minimal_roundtrip(tmp_path: Path) -> None:
    data = {
        "lab": {"name": "X", "contact": "a@b.org"},
        "auth": {"provider": "none"},
        "services": {"beacon": {"enabled": True}},
        "deploy": {"host": "localhost", "tls": False},
    }
    path = tmp_path / "stack.yml"
    path.write_text(yaml.safe_dump(data), encoding="utf-8")
    cfg = StackConfig.from_yaml(path)
    assert cfg.lab.name == "X"
    assert cfg.services.beacon.enabled is True
