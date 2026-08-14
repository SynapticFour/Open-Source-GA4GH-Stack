from __future__ import annotations

from pathlib import Path

from community_stack.compose_merge import merge_compose_files, strip_published_ports


def test_merge_composes_services_union(tmp_path: Path) -> None:
    a = tmp_path / "a.yml"
    b = tmp_path / "b.yml"
    a.write_text(
        """
services:
  a:
    image: test/a
volumes:
  va:
""",
        encoding="utf-8",
    )
    b.write_text(
        """
services:
  b:
    image: test/b
volumes:
  vb:
""",
        encoding="utf-8",
    )
    merged = merge_compose_files([a, b])
    assert set(merged["services"].keys()) == {"a", "b"}
    assert set(merged["volumes"].keys()) == {"va", "vb"}


def test_strip_published_ports(tmp_path: Path) -> None:
    compose = tmp_path / "c.yml"
    compose.write_text(
        """
services:
  beacon:
    image: x
    ports:
      - "5050:5050"
  oauth2-proxy:
    image: y
    ports:
      - "4180:4180"
""",
        encoding="utf-8",
    )
    data = strip_published_ports(merge_compose_files([compose]))
    assert "ports" not in data["services"]["beacon"]
    assert data["services"]["oauth2-proxy"]["ports"] == ["4180:4180"]
