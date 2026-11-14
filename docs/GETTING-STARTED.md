# Getting started

Two paths run from this repository. Neither starts [Ferrum Lab Kit](https://github.com/SynapticFour/Ferrum-Lab-Kit).

Prerequisites: Python 3.11 or newer (`cli/pyproject.toml`). The Beacon path also needs Docker.

## Check the CLI without starting containers

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e "./cli[dev]"
pytest cli/tests/
```

You should see the pytest summary. CI runs that, then `ruff check cli/src/ cli/tests/` and `mypy cli/src/ --strict`, on Python 3.11 and 3.12 (`.github/workflows/ci.yml`).

The package name is `ga4gh-community-stack`. The version in `cli/src/community_stack/__init__.py` is `0.1.0`. That number is not a status. The README recorded on 2026-09-05 that the package is not on PyPI. Install from this clone. Do not run `pip install ga4gh-community-stack`.

## Beacon

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e "./cli[dev]"
lab-stack init
lab-stack demo start
```

The documented address is `http://localhost:5050/ga4gh/beacon/v2`.

Or, after `make install`:

```bash
make up
make down      # stop; keep data
make destroy   # remove volumes
```

`lab-stack demo start` brings up Beacon and MongoDB. The Beacon image is Apache-2.0. The MongoDB image in `deploy/docker-compose/docker-compose.beacon.yml` is `mongo:5.0.32`, which is SSPL. That is not an OSI open-source licence. The component table on the README lists each image.
