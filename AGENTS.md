# AGENTS.md — Base44 sandbox notes

OpenDomain is a two-process monorepo: FastAPI in `backend/`, Next.js in `frontend/`.
These notes only cover what is not obvious from the manifests.

## Running it here

```bash
docker compose -f docker-compose.base44.yml up -d --build   # full stack
docker compose -f docker-compose.base44.yml ps               # service health
```

Do **not** use the repo's own `docker-compose.yml` in the sandbox: it builds the
packaging Dockerfiles and runs without the migrations/health ordering below.
`docker-compose.base44.yml` runs every application service from the bind-mounted
source: `uvicorn --reload` for the API, `next dev` for the web app.

- Dependencies install at container start (`uv pip install --system -e ".[dev]"`
  for the backend, `npm ci` for the frontend into a named `node_modules` volume),
  so a changed `pyproject.toml` / `package.json` needs a restart of that service
  (`docker compose -f docker-compose.base44.yml up -d backend frontend`).
- The `migrate` service is one-shot (`alembic upgrade head`) and the backend waits
  for it; re-run migrations with `docker compose -f docker-compose.base44.yml up -d migrate`.
- The backend sets `PYTHONPATH=/app` because the `uvicorn` console script does not
  put the working directory on `sys.path`, so `backend.app.main:app` will not
  import without it. The repo's Makefile does the same (`PYTHONPATH=. uvicorn …`).
- PowerDNS appears in the repo's own compose but no code path uses it
  (`dns_provider` / `powerdns_api_url` are configuration only), so it is omitted.

## Wiring that is easy to get wrong

- **Single origin.** The browser only talks to port 3000. `next.config.js`
  proxies `/api/*` to `API_PROXY_TARGET` (`http://backend:8000`), mirroring the
  production Caddy routing, and `NEXT_PUBLIC_API_URL` is deliberately left unset
  so the client uses relative URLs. This keeps the HttpOnly `opendomain_session`
  cookie (SameSite=lax) first-party; pointing `NEXT_PUBLIC_API_URL` at a
  browser-visible backend origin instead would make the session cross-site and
  break sign-in.
- `API_PROXY_TARGET` is a server-side-only addition to `frontend/next.config.js`.
  When it is unset, the rewrite behaves exactly as before (only
  `NEXT_PUBLIC_API_URL` matters), so local/production behaviour is unchanged.
- `allowedDevOrigins` is set to `3000-$BASE44_PUBLIC_HOST_SUFFIX` only when
  `BASE44_PREVIEW_MODE` is exactly `"1"`. Without it Next rejects the preview
  origin's dev assets and HMR. It takes a bare host, not a URL, and `'*'` does
  not match.
- `APP_URL`, `API_URL` and `CORS_ORIGINS` are built from
  `$BASE44_PUBLIC_HOST_SUFFIX` in compose, so nothing host-specific is committed.

## Verifying it works

- `curl -s http://localhost:3000/` → app HTML; `curl -s http://localhost:3000/api/health`
  → `{"status":"ok",...}` (proves the same-origin proxy); `curl -s http://localhost:8000/api/ready`
  → checks Postgres and Redis.
- Compose healthchecks: backend probes `/api/ready` with `python -c urllib`,
  frontend probes both its own page and `/api/health` through the proxy with
  `wget` and prints which half failed.
- There is no test suite on this branch (`tests/` is absent even though
  `CLAUDE.md` references it) and `npm test` in `frontend/` is a no-op, so backend
  checks are run directly, e.g. `docker compose -f docker-compose.base44.yml exec -T backend python -c "…"`.

## Sandbox limitations

- `RESEND_API_KEY` is unset, so `MailService` suppresses mail in development:
  verification and password-reset links are logged, never delivered. The email
  verification token only exists in that email, so a fresh registration cannot be
  completed end to end here.
- Sign-in always requires TOTP MFA and there is no seeded development account, so
  signed-in screens can only be checked with a session established by hand.
- `SECRET_KEY` is supplied by the platform at `/run/base44/app.env`; everything
  else falls back to development defaults in `backend/app/core/config.py`.
  `AUTH_ENCRYPTION_KEY` and `TOKEN_PEPPER` are derived from `SECRET_KEY` when
  unset (both are only mandatory when `ENVIRONMENT=production`).
- AWS/Bedrock credentials and EPP registry credentials are absent: the AI agent
  cannot reach Claude, and registration runs in simulated EPP mode
  (`EPP_SIMULATE=true`).
