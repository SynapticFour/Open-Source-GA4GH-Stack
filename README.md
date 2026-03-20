# GA4GH Community Stack

A curated deployment kit built from the best available **open-source GA4GH implementations** — modular, explicitly documented, and meant for **honest comparison** with integrated lab kits (e.g. Ferrum Lab Kit).

This repository is **not** a drop-in competitor to **Ferrum Lab Kit** (or similar commercial / integrated kits): it is the curated **open-source side** of the same architectural goals (Compose, Helm, SLURM/HPC). See **[COMPARISON.md](COMPARISON.md)** for a side-by-side view and **[docs/LIMITATIONS.md](docs/LIMITATIONS.md)** for where OSS integrations stop short of unified, passport-aware products.

**License:** MIT (this repo). **Upstream images:** MIT or Apache-2.0 as listed below. **Maintainer:** [Synaptic Four](https://synapticfour.dev).

---

## Fastest path to a running Beacon v2

From a clone of this repository (Docker required):

```bash
cd ga4gh-community-stack
python3 -m venv .venv && source .venv/bin/activate
pip install -e "./cli[dev]"   # or: pip install ga4gh-community-stack (when published)
lab-stack init
lab-stack demo start
# Beacon: http://localhost:5050/ga4gh/beacon/v2
```

Or use `./install.sh` once the package is on PyPI (installs `lab-stack` into your user environment).

---

## Who is this for?

The same audiences as Ferrum Lab Kit and comparable **GA4GH teaching / pilot** programmes: **core facilities**, **ELIXIR / GHGA / GDI-related pilots**, **HPC gateways**, and teams that need **standard APIs** (Beacon, WES, TES, DRS) without committing to a single vendor stack. The Community Stack is for labs that want **maximum upstream transparency** and are willing to own **heterogeneous configuration** across services.

---

## Components (pinned upstream)

| Component | Upstream | Container image | License |
|-----------|----------|-----------------|--------|
| **Beacon v2** | [EGA-archive/beacon2-pi-api](https://github.com/EGA-archive/beacon2-pi-api) | `egarchive/beacon2-pi-api:latest` | Apache-2.0 |
| **MongoDB (Beacon)** | — | `mongo:5.0.32` | SSPL — [MongoDB licensing](https://www.mongodb.com/legal/licensing/sspl) |
| **WES** | [sapporo-wes/sapporo-service](https://github.com/sapporo-wes/sapporo-service) | `ghcr.io/sapporo-wes/sapporo-service:latest` | Apache-2.0 |
| **TES** | [ohsu-comp-bio/funnel](https://github.com/ohsu-comp-bio/funnel) | `ohsucompbio/funnel:latest` | MIT |
| **DRS** | [ga4gh/ga4gh-starter-kit-drs](https://github.com/ga4gh/ga4gh-starter-kit-drs) | `ga4gh/ga4gh-starter-kit-drs:0.2.0` | Apache-2.0 |
| **OIDC gate** | [oauth2-proxy/oauth2-proxy](https://github.com/oauth2-proxy/oauth2-proxy) | `quay.io/oauth2-proxy/oauth2-proxy:latest` | MIT |
| **Reverse proxy** | [Caddy](https://caddyserver.com/) | `caddy:2-alpine` | Apache-2.0 |

Ingest tooling for Beacon: [beacon2-ri-tools-v2](https://github.com/EGA-archive/beacon2-ri-tools-v2) (see [docs/DATA-INGEST.md](docs/DATA-INGEST.md)).

---

## Capabilities vs limitations

**Strengths:** production-trusted Beacon and WES components, mature TES/SLURM story with Funnel, fully OSS, no license gate.

**Gaps (honest):** no built-in **GA4GH Passport / visa** enforcement at the edge; **heterogeneous config formats** per service; **DRS 1.3.0-experimental** in Starter Kit vs newer spec expectations elsewhere; no bundled **RO-Crate / provenance DAG** across WES↔DRS. Details: **[docs/LIMITATIONS.md](docs/LIMITATIONS.md)**.

---

## `lab-stack` CLI (overview)

| Command | Purpose |
|---------|---------|
| `lab-stack init` | Interactive wizard → `stack.yml` |
| `lab-stack generate compose` | Merge Compose fragments + render configs → `docker-compose.generated.yml` |
| `lab-stack generate helm` | Emit Helm values → `deploy/helm/values.generated.yaml` |
| `lab-stack generate systemd` | Copy SLURM-oriented units |
| `lab-stack status` | HTTP health table for enabled services |
| `lab-stack demo start` | Beacon + Mongo demo (uses `beacon-only.env`, demo-friendly oauth template) |
| `lab-stack demo seed` | Load `data/demo/*.json` into MongoDB |
| `lab-stack compare` | Open `COMPARISON.md` in `$PAGER` |

Configuration: **`stack.yml`** (structured) plus **`config/profiles/*.env`** for Compose-oriented toggles and secrets. See `stack.yml.example`.

---

## Repository layout

See the tree in the project brief: `deploy/docker-compose/` (fragments), `config/**` (templates), `deploy/helm/` (umbrella + subcharts), `deploy/slurm/`, `cli/`, `data/demo/`, `docs/`.

---

## Environment variable for non-standard checkout paths

```bash
export GA4GH_COMMUNITY_STACK_ROOT=/path/to/ga4gh-community-stack
```

---

## Contributing & CI

See [CONTRIBUTING.md](CONTRIBUTING.md). CI runs `pytest`, `ruff`, and `mypy --strict` on Python 3.11 and 3.12.

Documentation index: **[docs/COMPONENTS.md](docs/COMPONENTS.md)**, **[docs/ELIXIR-AAI.md](docs/ELIXIR-AAI.md)**, **[docs/SLURM-SETUP.md](docs/SLURM-SETUP.md)**.
