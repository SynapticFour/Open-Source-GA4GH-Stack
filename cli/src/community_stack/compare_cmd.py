from __future__ import annotations

import os
import shlex
import shutil
import subprocess
import sys

from community_stack.paths import comparison_markdown_path


def open_comparison() -> None:
    path = comparison_markdown_path()
    pager = os.environ.get("PAGER")
    if pager:
        subprocess.run([*shlex.split(pager), str(path)], check=False)
        return
    less = shutil.which("less")
    if less:
        subprocess.run([less, str(path)], check=False)
        return
    more = shutil.which("more")
    if more:
        subprocess.run([more, str(path)], check=False)
        return
    sys.stdout.write(path.read_text(encoding="utf-8"))
