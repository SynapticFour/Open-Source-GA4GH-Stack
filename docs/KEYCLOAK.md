# Keycloak (optional Compose fragment)

When `stack.yml` sets `auth.provider: keycloak`, `lab-stack generate compose` merges `deploy/docker-compose/docker-compose.keycloak.yml` and points **oauth2-proxy** at `auth.keycloak.issuer_url` (default `http://keycloak:8080/realms/master`).

## Setup outline

1. Run `lab-stack init` and choose **Keycloak**, or edit `stack.yml` and set `auth.keycloak.issuer_url` to your realm’s base URL (no trailing slash in YAML; a trailing slash is added for OIDC discovery in the proxy config).
2. In Keycloak, create an **OpenID Connect** confidential client; set **Valid redirect URIs** to `https://<host>/oauth2/callback` (or HTTP for local dev).
3. Put `client_id` / `client_secret` in `auth.ls_login` (same fields used for LS Login) or in profile `.env` as `LS_LOGIN_CLIENT_ID` / `LS_LOGIN_CLIENT_SECRET`.
4. `docker compose ... up` includes **Keycloak on port 8080** — adjust ports if your site collides.

The bundled image uses `start-dev` only for **labs**. Production Keycloak needs HA, TLS, and realm import via GitOps or operator patterns outside this repo.
