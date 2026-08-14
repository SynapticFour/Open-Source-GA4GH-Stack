from __future__ import annotations

from community_stack.config import StackConfig, merge_profile_env
from community_stack.profile_env import parse_bool


def test_parse_bool_truthy() -> None:
    for raw in ("1", "true", "TRUE", " yes ", "On"):
        assert parse_bool(raw) is True


def test_parse_bool_falsey() -> None:
    for raw in ("", "0", "false", "no", "off", None):
        assert parse_bool(raw) is False


def test_parse_bool_default() -> None:
    assert parse_bool(None, default=True) is True
    assert parse_bool("  ", default=True) is True


def test_merge_profile_yes_on() -> None:
    cfg = StackConfig()
    merged = merge_profile_env(
        cfg,
        {"INCLUDE_WES": "yes", "INCLUDE_TES": "on", "TLS": "on"},
    )
    assert merged.services.wes.enabled is True
    assert merged.services.tes.enabled is True
    assert merged.deploy.tls is True
