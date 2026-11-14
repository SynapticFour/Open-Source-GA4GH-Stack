# For evaluators

**Status: No public status is recorded.** The claims registry has no maturity stage for this kit. `0.1.0` in `cli/src/community_stack/__init__.py` is the package version.

This kit exists so a lab can compare upstream GA4GH services with [Ferrum Lab Kit](https://github.com/SynapticFour/Ferrum-Lab-Kit). The comparison is [COMPARISON.md](../COMPARISON.md).

## What a run shows

- `pytest cli/tests/` shows the CLI tests in this repository.
- `lab-stack demo start` shows Beacon and MongoDB. The documented Beacon address is `http://localhost:5050/ga4gh/beacon/v2`.
- A HelixTest run, when someone starts it, is a technical conformance signal for Beacon and, separately, for WES against Sapporo. [HELIXTEST.md](HELIXTEST.md) says that signal is not official GA4GH certification.

## What a run does not show

- The integration layer is MIT. Upstream images are not all MIT or Apache-2.0. MongoDB on the Beacon path is `mongo:5.0.32` under the SSPL (STACK-OSS-001). The prohibited sentence "100% OSS components" is not the wording for this kit.
- oauth2-proxy does not evaluate GA4GH Passports or Visas. [LIMITATIONS.md](LIMITATIONS.md), limitation 1.
- Caddy remains the floating tag `caddy:2-alpine`. Tag pins are not digest pins. Limitation 6.
- This kit does not ship a cross-service RO-Crate. Signed evidence stays in [HELIOS](https://github.com/SynapticFour/HELIOS).
- A green test run is not a clinical pilot and not a Synaptic Four production claim.

The limits in full are [LIMITATIONS.md](LIMITATIONS.md).
