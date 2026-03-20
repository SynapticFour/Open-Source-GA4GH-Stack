from __future__ import annotations

import os
import shutil
import subprocess

from community_stack.paths import find_repo_root


def open_comparison() -> None:
    path = find_repo_root() / "COMPARISON.md"
    if not path.is_file():
        raise FileNotFoundError(f"Missing {path}")

    pager = os.environ.get("PAGER") or shutil.which("less")
    if pager:
        subprocess.run([pager, str(path)], check=False)
    else:
        subprocess.run(["sh", "-c", f"more '{path}'"], check=False)
