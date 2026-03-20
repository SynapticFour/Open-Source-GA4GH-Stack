# Limitations (honest view)

This file is intentionally **not** marketing. It describes where the GA4GH Community Stack **stops** so labs can compare it fairly to integrated kits (e.g. Ferrum Lab Kit).

## Limitation 1: No GA4GH Passport / Visa evaluation at the edge

**oauth2-proxy** authenticates users via **OIDC** (e.g. ELIXIR LS Login) and issues session cookies. It does **not** parse or evaluate **GA4GH Passports** or **Visas** (e.g. `ControlledAccessGrant`, `ResearcherStatus`, `AffiliationAndRole`, etc.).

Implications:

- You can enforce “**someone is logged in**”, not “**this identity holds a Visa for dataset X**”.
- **Beacon v2** `controlled` access models that depend on **dataset-scoped authorisation** require **additional custom development** (e.g. a Passport-aware policy service in front of Beacon or native support inside the Beacon deployment), which this kit does **not** ship.

**Ferrum Lab Kit (positioning):** built-in evaluation of Passport Visas for controlled-access flows.

---

## Limitation 2: No single configuration schema across services

Each upstream chose its own configuration surface:

| Service | Format | Notes |
|---------|--------|--------|
| Beacon (beacon2-pi-api) | Python `conf.py` | Full language, not declarative YAML |
| Funnel (TES) | `funnel.conf` YAML | Distinct schema from other YAML |
| Sapporo (WES) | JSON + runtime flags | `executable_workflows.json` + env |
| Starter Kit DRS | `drs.config.yml` | Java/Spring Boot configuration tree |
| oauth2-proxy | INI / alpha config | Another dialect entirely |

**lab-stack** renders **templates** from one `stack.yml`, but anyone hand-editing configs still navigates **five conceptual formats**.

**Ferrum Lab Kit (positioning):** unified lab configuration (e.g. single TOML-style entry point).

---

## Limitation 3: DRS specification frozen on 1.3.0-experimental

The pinned image `ga4gh/ga4gh-starter-kit-drs:0.2.0` implements **DRS 1.3.0-experimental**. The broader GA4GH community is moving toward **DRS 1.4+**; interoperability guarantees with **DRS 1.4-first clients** are **not assured** from this stack alone.

**Ferrum Lab Kit (positioning):** tracks newer DRS in product releases.

---

## Limitation 4: Heterogeneous runtime and operations

Operational reality includes:

- **Languages:** Python services (Beacon, Sapporo), **Go** (Funnel), **Java** (DRS Starter Kit).
- **Datastores:** MongoDB for Beacon; SQLite or JDBC-backed stores for DRS; SQLite default for Sapporo/Funnel depending on deployment.
- **Health checks:** Different `/service-info` locations and semantics; **TES** may not mirror Beacon-style JSON for all endpoints.

On **HPC login nodes**, operating multiple runtimes and log formats is **more demanding** than a single stack with one primary observability story.

**Ferrum Lab Kit (positioning):** homogeneous Rust + Postgres operations story.

---

## Limitation 5: No cross-service provenance / RO-Crate story

Nothing in this kit automatically records a **DAG** of “**which WES run read which DRS objects**” suitable for publication compliance out of the box. Labs must bolt on workflow metadata, passports, and archival tooling themselves.

**Ferrum Lab Kit (positioning):** built-in **provenance** and **RO-Crate export** in product messaging.

---

## What the Community Stack is genuinely good at

- **Beacon v2:** `beacon2-pi-api` is widely exercised, plugin-capable (incl. EUCAIM / GA4GH models per upstream docs), and actively maintained by EGA.
- **WES:** **Sapporo** is one of the most **engine-complete** OSS WES implementations (Nextflow, Snakemake, CWL, WDL, Toil).
- **TES / SLURM:** **Funnel** is a production-grade choice for submitting work to **SLURM**, AWS Batch, Google Batch, HTCondor, and local Docker.
- **Licensing transparency:** MIT/Apache-2.0 upstreams without a commercial gate for the integration layer itself.
- **Credibility:** Components from recognised organisations (EGA, OHSU CompBio, GA4GH Starter Kit team, Sapporo maintainers).

---

## How we use this document

If a limitation here is a **hard requirement** for your pilot (Passport visas, DRS 1.4-only clients, single-schema ops), factor that into **kit selection** early. If the limitation is acceptable, you gain **upstream flexibility** at the cost of **integration labour** — a trade this repo documents rather than hiding.
