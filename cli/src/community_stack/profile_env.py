from __future__ import annotations

from pathlib import Path

_TRUE = frozenset({"1", "true", "yes", "on"})


def parse_bool(value: str | None, *, default: bool = False) -> bool:
    """Parse a profile / env flag. Accepts 1/true/yes/on (any case, stripped)."""
    if value is None:
        return default
    text = value.strip().lower()
    if not text:
        return default
    return text in _TRUE


def parse_dotenv(path: str | Path) -> dict[str, str]:
    out: dict[str, str] = {}
    text = Path(path).read_text(encoding="utf-8")
    for line in text.splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        if s.startswith("export "):
            s = s[7:].strip()
        if "=" not in s:
            continue
        key, val = s.split("=", 1)
        key = key.strip()
        val = val.strip().strip('"').strip("'")
        out[key] = val
    return out
