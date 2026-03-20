from __future__ import annotations

import os
import shutil
import subprocess

from community_stack.paths import comparison_markdown_path


def open_comparison() -> None:
    path = comparison_markdown_path()

    pager = os.environ.get("PAGER") or shutil.which("less")
    if pager:
        subprocess.run([pager, str(path)], check=False)
    else:
        subprocess.run(["sh", "-c", f"more '{path}'"], check=False)
