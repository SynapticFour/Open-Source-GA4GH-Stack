# ELIXIR LS Login and oauth2-proxy

This stack uses **[oauth2-proxy](https://github.com/oauth2-proxy/oauth2-proxy)** as a **practical** OIDC gate in front of Beacon (and optionally via Caddy for multi-service paths). The default OIDC issuer in templates is **ELIXIR Czech LS Login**:

- **OIDC discovery:** `https://login.elixir-czech.org/oidc/`

## What you get

- Browser-oriented **login** with standard OIDC claims (e.g. `email`, `sub`).
- Cookie-based session management at the proxy.
- Configurable **skip** routes for public metadata such as Beacon **`service-info`** and **`info`**.

Templates live in `config/oauth2-proxy/oauth2-proxy.cfg.template`. **`lab-stack generate compose`** substitutes:

- `client_id`, `client_secret`
- `redirect_url` derived from `stack.yml` `deploy.host` + `deploy.tls`
- `cookie_secret` (must be strong in production)
- Optional **demo** mode injecting `skip_auth_regex` (see [LIMITATIONS.md](LIMITATIONS.md))

## What you do *not* get

oauth2-proxy does **not**:

- Parse **GA4GH Passports** from tokens.
- Evaluate **Visas** (`ControlledAccessGrant`, etc.) against **dataset identifiers** in Beacon queries.
- Provide **dataset-scoped** authorisation suitable for regulated controlled-access releases without **additional services**.

For Passport-aware access, you need either:

- Native support inside the data service (Beacon deployment / database policies), **or**
- A **Passport-aware policy engine** (custom or productised) in the request path.

Read the honest gap list in **[LIMITATIONS.md](LIMITATIONS.md), Limitation 1**.

## Production checklist

- Register a confidential client with LS Login; set **exact redirect URL** to `https://<host>/oauth2/callback` (or HTTP for local dev only).
- Use a **32+ byte** random `cookie_secret`.
- Prefer **TLS** at Caddy and set `cookie_secure = true`.
- Review **`skip_auth_routes`** — every regex is a **public** bypass of the gate.
