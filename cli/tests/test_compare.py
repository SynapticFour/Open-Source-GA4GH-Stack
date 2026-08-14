from __future__ import annotations

from pathlib import Path

import pytest

from community_stack.compare_cmd import open_comparison


def test_pager_is_split(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    md = tmp_path / "COMPARISON.md"
    md.write_text("# x\n", encoding="utf-8")
    monkeypatch.setenv("PAGER", "less -R")
    monkeypatch.setattr(
        "community_stack.compare_cmd.comparison_markdown_path",
        lambda: md,
    )
    seen: list[list[str]] = []

    def fake_run(cmd: list[str], **_kwargs: object) -> None:
        seen.append(cmd)

    monkeypatch.setattr("community_stack.compare_cmd.subprocess.run", fake_run)
    open_comparison()
    assert seen[0][:3] == ["less", "-R", str(md)]
