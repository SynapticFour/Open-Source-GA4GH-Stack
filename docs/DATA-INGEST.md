# Beacon data ingest (`beacon2-ri-tools-v2`)

Production Beacon deployments normally load **VCF → JSON** pipelines compatible with beacon2-pi-api’s MongoDB schema using the EGA **Reference Implementation tools**:

- **Repository:** [EGA-archive/beacon2-ri-tools-v2](https://github.com/EGA-archive/beacon2-ri-tools-v2)
- **Published container (example tag in upstream compose):** `ghcr.io/ega-archive/beacon2-ri-tools-v2:2.0.6`

This Community Stack ships **small JSON fixtures** under `data/demo/` and a **`lab-stack demo seed`** path that runs `mongoimport` for local smoke testing. That path is **not** a substitute for full **VCF validation**, **cohort modelling**, or **controlled-access** governance.

## Recommended flow (high level)

1. Prepare **datasets / cohorts / individuals / genomic variations** per Beacon v2 models (see GA4GH models and EGA RI documentation).
2. Run **RI tools** with configuration pointing at your MongoDB host (often the `mongodb` service in Compose).
3. Verify **`/service-info`**, **`/filtering_terms`**, and representative queries return expected `exists` / `count` / `records` granularities.

## Demo JSON only

Files in `data/demo/` exist so `lab-stack demo start` + `demo seed` can prove **API reachability** on a laptop. They may **not** satisfy every Beacon v2 validation rule your UI or network applies — treat them as **scaffolding**, not reference biomedical content.

## Security note

Ingest tooling can process **sensitive** genetic data. Run it in **approved environments** with appropriate **access controls**; do not pointed-at production MongoDB clusters from untrusted networks.
