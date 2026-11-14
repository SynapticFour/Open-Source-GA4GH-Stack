# Architecture

This page is how the kit is composed. Each service stays an upstream project. This repository is the integration layer.

## Primary references

- [COMPONENTS.md](COMPONENTS.md): upstream services, versions, and integration points
- [LIMITATIONS.md](LIMITATIONS.md): known platform boundaries and operational trade-offs
- [SLURM-SETUP.md](SLURM-SETUP.md): TES/Funnel execution model in HPC environments
- [ELIXIR-AAI.md](ELIXIR-AAI.md): identity and reverse-proxy integration model

## Design principles

- Keep composition explicit: each service remains traceable to an upstream project.
- Prefer reproducible deployment artifacts over implicit local conventions.
- Keep security and interoperability boundaries visible in docs and configuration.

## Licence boundary

The integration layer in this repository is MIT. Upstream images are not one OSI set. The Beacon path runs MongoDB `mongo:5.0.32` under the SSPL. The component table in the README is the list, including Caddy on the floating tag `caddy:2-alpine` and Starter Kit DRS `0.2.0`.
