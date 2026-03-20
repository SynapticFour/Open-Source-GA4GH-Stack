# Contributing

Thank you for helping improve the GA4GH Community Stack.

## Principles

- Keep comparisons with other kits factual; cite upstream docs and versions.
- Prefer small, focused changes with clear rationale.
- Match existing style in Python (ruff), YAML, and Markdown.

## Development setup

```bash
cd cli
pip install -e ".[dev]"
pytest tests/
ruff check src/
mypy src/ --strict
```

## Pull requests

- Describe what problem the change solves.
- For behaviour changes, update relevant docs (`docs/`, `README.md`).
- CI runs tests, Ruff, and mypy on Python 3.11 and 3.12.
