from __future__ import annotations

from community_stack.config import StackConfig
from community_stack.status_cmd import extract_version, probes_for_stack


def test_probes_localhost_when_ungated() -> None:
    cfg = StackConfig.model_validate(
        {
            "auth": {"provider": "none"},
            "services": {"beacon": {"enabled": True}},
            "deploy": {"host": "beacon.example.org", "tls": False},
        }
    )
    urls = [p.url for p in probes_for_stack(cfg, {})]
    assert "http://localhost:5050/ga4gh/beacon/v2/service-info" in urls


def test_probes_gateway_when_gated() -> None:
    cfg = StackConfig.model_validate(
        {
            "auth": {"provider": "ls-login"},
            "services": {
                "beacon": {"enabled": True},
                "tes": {"enabled": True, "backend": "local"},
            },
            "deploy": {"host": "beacon.example.org", "tls": True},
        }
    )
    probes = {p.name: p.url for p in probes_for_stack(cfg, {})}
    assert probes["Beacon v2"] == "https://beacon.example.org/ga4gh/beacon/v2/service-info"
    assert probes["TES"] == "https://beacon.example.org/ga4gh/tes/v1/tasks"


def test_extract_version_tes_not_invented() -> None:
    assert extract_version("tes", []) == "—"
    assert extract_version("ga4gh", {"type": {"version": "2.0"}}) == "2.0"
