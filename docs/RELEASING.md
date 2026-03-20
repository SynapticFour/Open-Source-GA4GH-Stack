# Releasing `ga4gh-community-stack`

## Wheel contents

The package bundles deploy templates under `community_stack/_bundled/` so `lab-stack generate` works after `pip install` without a separate git clone. Verify locally:

```bash
cd cli
pip install hatch
hatch build
python -m zipfile -l dist/ga4gh_community_stack-*.whl | head
# expect community_stack/_bundled/deploy/docker-compose/...
```

## PyPI (trusted publishing)

1. Create the project on [PyPI](https://pypi.org/) (first upload may use `twine` + API token once).
2. In PyPI → **Publishing** → add a **trusted publisher** for GitHub `SynapticFour/Open-Source-GA4GH-Stack` and workflow `publish-pypi.yml`.
3. Publish a **GitHub Release** or run **Actions → Publish PyPI → Run workflow** (restricted to `repository_owner == SynapticFour`).

If OIDC is not configured yet, publish manually:

```bash
cd cli && hatch build && python -m twine upload dist/*
```

## Version bump

Edit `cli/src/community_stack/__init__.py` and `cli/pyproject.toml` `version` field together.
