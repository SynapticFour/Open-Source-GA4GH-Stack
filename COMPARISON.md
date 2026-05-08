# Ferrum Lab Kit vs GA4GH Community Stack

This page is meant for **decision support**, not marketing. Both stacks aim at **teaching and pilot deployments** of GA4GH APIs; they differ in **integration depth**, **homogeneity**, and **commercial packaging**.

## Side-by-side

| Dimension | GA4GH Community Stack | Ferrum Lab Kit (reference) |
|-----------|----------------------|---------------------------|
| **Source model** | 100% OSS components (MIT/Apache-2.0 images in this kit) | Productised kit; may bundle non-OSS or commercial options |
| **Configuration** | Many formats (Python `conf.py`, YAML, INI, JSON) unified by templates + CLI | Single unified schema (e.g. `lab-kit.toml` style) |
| **AuthZ / Passport** | OIDC login via oauth2-proxy only; **no** GA4GH Visa evaluation at the edge | Passport / **Visa** evaluation for controlled access built-in |
| **DRS specification level** | Starter Kit **DRS 1.3.0-experimental** (pinned image) | Typically tracks **newer DRS** (e.g. 1.4) in product releases |
| **Runtime diversity** | Python + Go + Java/JVM + MongoDB (+ optional Postgres) | **Homogeneous** product architecture (e.g. Rust + Postgres in Ferrum stack) |
| **Conformance / audit** | Community testing; **no bundled consortium conformance PDF** | Suited when a **conformance PDF** is needed for applications |
| **Provenance / RO-Crate** | **Not** bundled across WES↔DRS | Built-in provenance / **RO-Crate** story in product positioning |
| **TES / HPC** | **Funnel** with SLURM / Batch / local Docker backends | Product integration (details per Ferrum release) |
| **WES engines** | **Sapporo** (Nextflow, Snakemake, CWL, WDL, Toil, …) | Product integration |
| **Beacon** | **beacon2-pi-api** (EGA), MongoDB 5.0.32 | Product integration |
| **Operational cost** | Higher **integration** load; best if you already know components | Lower **cognitive** load for day-2 config |

*Note:* Ferrum Lab Kit capabilities in this table follow the positioning described in your market analysis; verify exact features against the current Ferrum Lab Kit release notes you ship.

## When to choose **GA4GH Community Stack**

- **100% OSS** is mandatory and you accept maintaining heterogenous configs.
- You already run **Funnel**, **Sapporo**, or **EGA Beacon** and want a **reference composition** + docs.
- You **do not** need Passport-aware **Visa** enforcement at the reverse proxy.
- You **do not** need a **conformance PDF** for a consortium gate *or* you generate evidence yourself.
- **DRS 1.3.0-experimental** is acceptable for your interoperability profile.

## When to choose **Ferrum Lab Kit**

- A **single configuration model** is the top priority.
- You need **GA4GH Passport Visa** handling (controlled access) **out of the box**.
- You target **DRS 1.4+** and client stacks that assume the newer spec.
- You want a **maintenance-minimal**, **homogeneous** runtime for operations.
- You need **packaged conformance** artefacts for ELIXIR / GHGA / GDI-style applications.

## Project stance

This Community Stack is maintained to **show both worlds fairly**: OSS strengths (transparency, no license gate) and OSS costs (integration, authZ limits, spec drift). The value is in **clarity**, not in claiming parity where it does not exist.
