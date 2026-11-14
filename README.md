# GA4GH Community Stack

This kit runs upstream GA4GH services side by side, so a lab can compare that arrangement with an integrated lab kit.

For a core facility, a teaching lab, or a pilot team that wants each service to stay an upstream project and is willing to own the differences between them.

**Status: No public status is recorded.** The claims registry has no maturity stage for this kit. Registry for the licence boundary: STACK-OSS-001. The package version in `cli/src/community_stack/__init__.py` is 0.1.0. That number is not a status.

The integration layer in this repository is MIT. Upstream images are not one OSI set. The Beacon path includes MongoDB under the SSPL. That is not an OSI open-source licence.

This kit does not replace [Ferrum Lab Kit](https://github.com/SynapticFour/Ferrum-Lab-Kit). The comparison is [COMPARISON.md](COMPARISON.md).

> This repository documents technical capabilities and operating guidance. It is not legal advice and does not by itself provide regulatory certification or compliance guarantees.

## What it does

- `lab-stack` renders Compose, Helm, or systemd from one `stack.yml`. GA4GH is a set of shared interfaces for genomic and health data. This kit runs Beacon v2, WES, TES, and DRS as separate upstream services.
- `lab-stack demo start` starts Beacon and MongoDB. The documented Beacon address is `http://localhost:5050/ga4gh/beacon/v2`.
- HelixTest, when a job is started, is a technical signal for Beacon and for WES. It is not a GA4GH certification. [docs/HELIXTEST.md](docs/HELIXTEST.md).

## Limits

- The integration layer is MIT. Upstream images are not all MIT or Apache-2.0. MongoDB on the Beacon path is `mongo:5.0.32` under the SSPL (STACK-OSS-001). The sentence "100% OSS components" is not the wording for this kit.
- There is no GA4GH Passport or Visa check at the edge. oauth2-proxy checks that someone is signed in. [docs/LIMITATIONS.md](docs/LIMITATIONS.md).
- Starter Kit DRS `0.2.0` is DRS 1.3.0-experimental. Caddy stays on the floating tag `caddy:2-alpine`.
- This kit does not ship RO-Crate or a signed evidence trail. That stays in [HELIOS](https://github.com/SynapticFour/HELIOS).
- `ga4gh-community-stack` was recorded on 2026-09-05 as not on PyPI. Install from this clone.

The component table:

| Component | Upstream | Container image | License |
|-----------|----------|-----------------|--------|
| **Beacon v2** | [EGA-archive/beacon2-pi-api](https://github.com/EGA-archive/beacon2-pi-api) | `ghcr.io/ega-archive/beacon2-pi-api:v2.1.2` (pinned; see compose) | Apache-2.0 |
| **MongoDB (Beacon)** | — | `mongo:5.0.32` | SSPL — [MongoDB licensing](https://www.mongodb.com/legal/licensing/sspl) |
| **WES** | [sapporo-wes/sapporo-service](https://github.com/sapporo-wes/sapporo-service) | `ghcr.io/sapporo-wes/sapporo-service:2.2.6` | Apache-2.0 |
| **TES** | [ohsu-comp-bio/funnel](https://github.com/ohsu-comp-bio/funnel) | `ohsucompbio/funnel:0.10.1` | MIT |
| **DRS** | [ga4gh/ga4gh-starter-kit-drs](https://github.com/ga4gh/ga4gh-starter-kit-drs) | `ga4gh/ga4gh-starter-kit-drs:0.2.0` | Apache-2.0 |
| **OIDC gate** | [oauth2-proxy/oauth2-proxy](https://github.com/oauth2-proxy/oauth2-proxy) | `quay.io/oauth2-proxy/oauth2-proxy:v7.15.4` | MIT |
| **Reverse proxy** | [Caddy](https://caddyserver.com/) | `caddy:2-alpine` | Apache-2.0 |

Ingest tooling for Beacon: [beacon2-ri-tools-v2](https://github.com/EGA-archive/beacon2-ri-tools-v2). See [docs/DATA-INGEST.md](docs/DATA-INGEST.md).

## Quick start

Prerequisites: Python 3.11 or newer, and Docker for the Beacon path.

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e "./cli[dev]"
pytest cli/tests/
lab-stack demo start
```

You should see the pytest summary, then Beacon at `http://localhost:5050/ga4gh/beacon/v2`. Stop with `lab-stack demo stop`, or `make down` after `make install`. Remove volumes with `make destroy`.

The steps are in [docs/GETTING-STARTED.md](docs/GETTING-STARTED.md).

`lab-stack` commands (`init`, `generate`, `status`, `demo`, `compare`) are listed in [docs/GETTING-STARTED.md](docs/GETTING-STARTED.md) and in the previous command table below.

| Command | Purpose |
|---------|---------|
| `lab-stack init` | Interactive wizard → `stack.yml` |
| `lab-stack generate` | Dispatch to compose / helm / systemd from `stack.yml` `deploy.target` |
| `lab-stack generate compose` | Merge Compose fragments + render configs → `docker-compose.generated.yml` |
| `lab-stack generate helm` | Copy Helm charts + emit `deploy/helm/values.generated.yaml` |
| `lab-stack generate systemd` | Copy SLURM-oriented units |
| `lab-stack status` | HTTP health table for enabled services |
| `lab-stack demo start` | Beacon + Mongo demo (uses `beacon-only.env`, demo-friendly oauth template) |
| `lab-stack demo stop` | Stop demo stack; keep volumes |
| `lab-stack demo destroy` | Stop demo stack; remove volumes |
| `lab-stack demo seed` | Load `data/demo/*.json` into MongoDB |
| `lab-stack compare` | Open `COMPARISON.md` in `$PAGER` |

Configuration: `stack.yml` plus `config/profiles/*.env`. See `stack.yml.example`.

For a checkout that is not the default directory:

```bash
export GA4GH_COMMUNITY_STACK_ROOT=/path/to/ga4gh-community-stack
```

## Documentation

### Tutorial

- [Getting started](docs/GETTING-STARTED.md)

### How-to guides

- [Data ingest](docs/DATA-INGEST.md)
- [ELIXIR AAI](docs/ELIXIR-AAI.md)
- [HelixTest](docs/HELIXTEST.md)
- [Keycloak](docs/KEYCLOAK.md)
- [SLURM](docs/SLURM-SETUP.md)
- [Releasing](docs/RELEASING.md)

### Reference

- [Components](docs/COMPONENTS.md)
- [For evaluators](docs/FOR-EVALUATORS.md)
- [Limitations](docs/LIMITATIONS.md)
- [Comparison](COMPARISON.md)
- [Changelog](CHANGELOG.md)

### Explanation

- [Architecture](docs/ARCHITECTURE.md)
- [Decisions](DECISIONS.md)

The full index is [docs/README.md](docs/README.md).

German: [README.de.md](README.de.md).

## Licence

The integration layer is the MIT License: use, copy, modify, and distribute it, with the copyright notice kept. The file is [LICENSE](LICENSE). Upstream images keep the licences in the table above, including MongoDB under the SSPL.

## Cite

Use [CITATION.cff](CITATION.cff). Prefer that file over a hand-copied line.

## Website

- Open source: [https://synapticfour.com/en/opensource/](https://synapticfour.com/en/opensource/)
- Technical profile: [https://synapticfour.com/en/technical/code/](https://synapticfour.com/en/technical/code/)

The same pages exist in German (`/de/opensource/`, `/de/technik/code/`) and in French (`/fr/opensource/`, `/fr/technique/code/`).

The map of repositories: [profile/README.md](https://github.com/SynapticFour/.github/blob/main/profile/README.md).

Contact: [contact@synapticfour.com](mailto:contact@synapticfour.com)
