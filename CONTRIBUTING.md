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

## Conformance (HelixTest)

HelixTest CI: Phase 1 Beacon in [`.github/workflows/helixtest-phase1.yml`](.github/workflows/helixtest-phase1.yml), Phase 2 WES (Sapporo) in [`.github/workflows/helixtest-phase2-wes.yml`](.github/workflows/helixtest-phase2-wes.yml). How to reproduce locally, URL schema, and env vars: **[docs/HELIXTEST.md](docs/HELIXTEST.md)**.

## Releases

See [docs/RELEASING.md](docs/RELEASING.md) for wheel layout, PyPI trusted publishing, and version bumps.
