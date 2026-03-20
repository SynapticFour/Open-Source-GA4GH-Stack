# Upstream components

Exact versions and images are pinned in the root **README** and Compose fragments under `deploy/docker-compose/`. This page summarises **roles** and **documentation entry points**.

## Beacon v2 — `beacon2-pi-api`

- **Repository:** [EGA-archive/beacon2-pi-api](https://github.com/EGA-archive/beacon2-pi-api)
- **Image:** `ghcr.io/ega-archive/beacon2-pi-api:latest` (GHCR — [package](https://github.com/EGA-archive/beacon2-pi-api/pkgs/container/beacon2-pi-api); the Docker Hub name `egarchive/...` is not used for public pulls)
- **Datastore:** MongoDB **5.0.32** (Compose default)
- **Config:** Python module at `beacon/conf/conf.py` (mounted from `config/beacon/conf.py` in this kit). **Mongo connection** is via `beacon/connections/mongo/conf.env` (mounted from `config/beacon/mongo/conf.env`).
- **Ingest:** [beacon2-ri-tools-v2](https://github.com/EGA-archive/beacon2-ri-tools-v2)
- **Ports:** `5050` (HTTP API), Mongo `27017` internal to Compose network.

## WES — Sapporo

- **Repository:** [sapporo-wes/sapporo-service](https://github.com/sapporo-wes/sapporo-service)
- **Image:** `ghcr.io/sapporo-wes/sapporo-service:latest`
- **Spec:** WES **1.1.0** (per upstream Sapporo 2.x line)
- **Engines:** Nextflow, Snakemake, CWL (`cwltool`), WDL (Cromwell), Toil (see Sapporo docs)
- **Config:** `executable_workflows.json` + environment (`SAPPORO_HOST`, `SAPPORO_PORT`).
- **Port:** `1122` (Swagger UI typically at `/docs` when enabled upstream).

## TES — Funnel

- **Repository:** [ohsu-comp-bio/funnel](https://github.com/ohsu-comp-bio/funnel)
- **Image:** `ohsucompbio/funnel:latest`
- **Config:** `funnel.conf` YAML.
- **Ports:** `8000` (HTTP), `9090` (gRPC).
- **Backends:** Docker (local dev), **SLURM**, HTCondor, AWS Batch, Google Cloud Batch.

## DRS — GA4GH Starter Kit

- **Repository:** [ga4gh/ga4gh-starter-kit-drs](https://github.com/ga4gh/ga4gh-starter-kit-drs)
- **Image:** `ga4gh/ga4gh-starter-kit-drs:0.2.0`
- **Spec level:** **DRS 1.3.0-experimental** (see [LIMITATIONS.md](LIMITATIONS.md))
- **Ports:** `4500` (public), `4501` (admin).

## Optional IdP — Keycloak (Compose)

- **Fragment:** `deploy/docker-compose/docker-compose.keycloak.yml` (merged when `auth.provider: keycloak`).
- **Docs:** [KEYCLOAK.md](KEYCLOAK.md)

## Edge authentication — oauth2-proxy

- **Repository:** [oauth2-proxy/oauth2-proxy](https://github.com/oauth2-proxy/oauth2-proxy)
- **Image:** `quay.io/oauth2-proxy/oauth2-proxy:latest`
- **Role:** OIDC **authentication** in front of HTTP upstreams. **Not** GA4GH Passport-aware (see [LIMITATIONS.md](LIMITATIONS.md)).

## Reverse proxy — Caddy 2

- **Project:** [Caddy](https://caddyserver.com/)
- **Image:** `caddy:2-alpine`
- **Role:** Single-host routing to `/ga4gh/...` paths and `/oauth2/...` for the proxy.
