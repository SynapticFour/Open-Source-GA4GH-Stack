# HelixTest integration (Phase 1 — Beacon)

This repository runs **[HelixTest](https://github.com/SynapticFour/HelixTest)** in CI as a **technical conformance signal** for **Beacon v2** only. It is **not** official GA4GH certification; see HelixTest’s own disclaimer.

For a **full** GA4GH matrix (WES, TES, DRS, Beacon, htsget, auth, Crypt4GH, etc.) against an integrated stack, see **[Ferrum](https://github.com/SynapticFour/Ferrum)** and its conformance docs (e.g. `docs/HELIXTEST-INTEGRATION.md` there).

---

## What runs in GitHub Actions

Workflow: **[`.github/workflows/helixtest-phase1.yml`](../.github/workflows/helixtest-phase1.yml)**  
Job: `beacon-safe-subset` (on `push` / `pull_request` to `main`, or **workflow_dispatch**).

Rough sequence:

1. Checkout this repo, install the **`lab-stack`** CLI (`pip install -e "./cli"`).
2. **Generate** Compose into a temp dir (same as CI):
   - `lab-stack generate compose --config config/profiles/beacon-only.env --output /tmp/ga4gh-cs`
3. **Start** only `beacon` and `mongodb`:
   - `docker compose -f …/docker-compose.generated.yml --project-directory /tmp/ga4gh-cs up -d beacon mongodb`
4. **Wait** until Beacon answers:
   - `GET http://localhost:5050/ga4gh/beacon/v2/service-info` → HTTP 200
5. **Seed** MongoDB with demo JSON (same collections as `lab-stack demo seed`):
   - `datasets`, `cohorts`, `individuals`, `genomicVariations` from `/demo/*.json` inside the Mongo container.
6. Checkout **HelixTest** (`SynapticFour/HelixTest`), then run:
   - `cargo run --bin helixtest -- --all --mode ferrum --only beacon --verbose --report json --fail-level 0`
7. Upload **`helix-report-phase1`** artifact (JSON report path in workflow: `/tmp/helix-report-phase1.json`).
8. **Tear down** Compose (`down -v`).

The HelixTest step uses **`continue-on-error: true`** so a failing report does not block the workflow; the artifact still captures the outcome.

---

## Beacon URL schema (Community Stack)

Generated **`config/beacon/conf.py`** sets **`uri_subpath = "/ga4gh/beacon/v2"`** so [beacon2-pi-api](https://github.com/EGA-archive/beacon2-pi-api) exposes routes under the GA4GH v2 prefix (not only under `/api/...`).

| Concept | Value |
|--------|--------|
| **Host (Compose default)** | `localhost` |
| **Beacon container port** | `5050` → mapped to host `5050` |
| **Base URL for HelixTest** | `http://localhost:5050/ga4gh/beacon/v2` |
| **Service info** | `GET http://localhost:5050/ga4gh/beacon/v2/service-info` |
| **Example query** | `POST http://localhost:5050/ga4gh/beacon/v2/query` (Beacon v2 JSON body) |

Behind **Caddy** (full `beacon-only` profile with base), the same paths are usually reached via the site host, e.g. `http://<HOST>/ga4gh/beacon/v2/...` — see [`config/caddy/Caddyfile.template`](../config/caddy/Caddyfile.template).

---

## Environment variables (HelixTest)

HelixTest reads service bases from **[`TestConfig`](https://github.com/SynapticFour/HelixTest)** (`helixtest/crates/common/src/config.rs`):

| Variable | Used in Phase 1 workflow |
|----------|---------------------------|
| **`BEACON_URL`** | `http://localhost:5050/ga4gh/beacon/v2` |

Other URLs (`WES_URL`, `TES_URL`, …) are **not** set in Phase 1 because only Beacon containers start.

---

## Why `--mode ferrum` (not `generic`)

In **`generic`** mode, HelixTest’s runner first probes **WES** at `{wes_url}/service-info` to auto-detect a Ferrum-style deployment. The default `wes_url` is `http://localhost:8080`, which **nothing listens on** in the Beacon-only Compose profile — so the run appears to “hang” on retries.

**`--mode ferrum`** skips that probe and goes straight to the Beacon checks, which matches our CI stack.

Naming is historical (“Ferrum mode” in HelixTest); here it only means **skip WES auto-detect**, not “this IS Ferrum”.

---

## Reproduce locally (minimal)

Prerequisites: **Docker**, **Rust** (stable), **Python 3.11+**, repo clone.

```bash
# 1) CLI
pip install -e "./cli"

# 2) Generate (pick a project dir; CI uses /tmp/ga4gh-cs)
OUT="$PWD/_helixtest-repro"
lab-stack generate compose --config config/profiles/beacon-only.env --output "$OUT"

# 3) Start Beacon + Mongo
docker compose -f "$OUT/docker-compose.generated.yml" --project-directory "$OUT" up -d beacon mongodb

# 4) Wait for service-info
until curl -fsS http://localhost:5050/ga4gh/beacon/v2/service-info >/dev/null; do sleep 2; done

# 5) Seed Mongo (same as lab-stack demo seed)
lab-stack demo seed   # finds compose under cwd or uses bundled assets; or run mongoimport like CI

# 6) HelixTest
git clone --depth 1 https://github.com/SynapticFour/HelixTest.git /tmp/HelixTest
cd /tmp/HelixTest/helixtest
export BEACON_URL=http://localhost:5050/ga4gh/beacon/v2
cargo run --bin helixtest -- --all --mode ferrum --only beacon --verbose --report json --fail-level 0

# 7) Cleanup
cd -
docker compose -f "$OUT/docker-compose.generated.yml" --project-directory "$OUT" down -v
```

If `lab-stack demo seed` does not find your generated project, run **`mongoimport`** from the workflow (step “Seed Beacon demo data”) with `--project-directory "$OUT"` and password from `"$OUT/.env"` (`MONGO_PASSWORD=`).

---

## Related workflows

| Workflow | Role |
|----------|------|
| [`compose-smoke.yml`](../.github/workflows/compose-smoke.yml) | Validates generated Compose and waits for Beacon `service-info` (no HelixTest). |
| [`helixtest-phase1.yml`](../.github/workflows/helixtest-phase1.yml) | Beacon + seed + HelixTest + artifact. |

---

## Future extensions (not implemented here)

- HelixTest against **WES / TES / DRS** when a stable multi-service profile and seed data exist.
- Optional **`HELIXTEST_PROFILE`** / **`HELIXTEST_CONFIG`** for HelixTest (see upstream) if we add checked-in TOML profiles for this stack.
