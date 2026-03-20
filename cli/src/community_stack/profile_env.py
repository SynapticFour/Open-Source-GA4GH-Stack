from __future__ import annotations

from pathlib import Path


def parse_dotenv(path: str | Path) -> dict[str, str]:
    out: dict[str, str] = {}
    text = Path(path).read_text(encoding="utf-8")
    for line in text.splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        if "=" not in s:
            continue
        key, val = s.split("=", 1)
        key = key.strip()
        val = val.strip().strip('"').strip("'")
        out[key] = val
    return out
