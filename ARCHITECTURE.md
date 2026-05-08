# Architecture

This root document is an index for architecture-relevant references in this repository.

## Primary references

- `docs/COMPONENTS.md`: upstream services, versions, and integration points
- `docs/LIMITATIONS.md`: known platform boundaries and operational trade-offs
- `docs/SLURM-SETUP.md`: TES/Funnel execution model in HPC environments
- `docs/ELIXIR-AAI.md`: identity and reverse-proxy integration model

## Design principles

- Keep composition explicit: each service remains traceable to an upstream project.
- Prefer reproducible deployment artifacts over implicit local conventions.
- Keep security and interoperability boundaries visible in docs and configuration.
