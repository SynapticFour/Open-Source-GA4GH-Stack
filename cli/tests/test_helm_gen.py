from __future__ import annotations

import click
import pytest

from community_stack.config import StackConfig
from community_stack.helm_gen import build_values


def test_build_values_mongo_from_profile() -> None:
    cfg = StackConfig.model_validate({"services": {"beacon": {"enabled": True}}})
    values = build_values(cfg, {"MONGO_PASSWORD": "secret-mongo"})
    assert values["beacon"]["mongo"]["password"] == "secret-mongo"
    assert "mongo_password" not in values["beacon"]


def test_build_values_rejects_kubernetes() -> None:
    cfg = StackConfig.model_validate(
        {"services": {"tes": {"enabled": True, "backend": "kubernetes"}}}
    )
    with pytest.raises(click.ClickException, match="kubernetes"):
        build_values(cfg)
