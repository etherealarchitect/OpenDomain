# Working notes for agents

Facts that are not obvious from the manifests. Day-to-day commands live in the README/Makefile.

## Running this repo in the Base44 sandbox

`docker-compose.base44.yml` is the sandbox runbook (the repo's own `docker-compose.yml` runs
prebuilt-style images and is not used here):

```bash
docker compose -f docker-compose.base44.yml up -d --build
```

- Web entry point: host port **3000** (Next.js dev server). API: host port **8000** (uvicorn `--reload`).
- `db` (PostgreSQL) and `redis` are plain services; `migrate` runs `alembic upgrade head` once and
  `backend` waits for it to complete. Re-running migrations is safe (`up -d`).
- Source is bind-mounted into both app services, so edits reload without a rebuild. Dependency
  changes do not: rerun `up -d --build` (backend) or restart `frontend` (it runs `npm ci` on start).
- PowerDNS is deliberately absent: no application code calls it (only `POWERDNS_*` settings exist)
  and its `gpgsql` schema is not migrated. Redis *is* required — auth rate limiting uses it.

### Known pitfalls

- The repo's own `docker-compose.yml` (and `make dev`) declares `env_file: .env`, and `.env` is
  gitignored — a fresh clone fails immediately with `env file /app/.env not found` until
  `.env.example` is copied. The sandbox stack avoids that by using `.env.base44-defaults`.
- **Never run `npm run build` inside the running `frontend` container.** The dev server and the
  production build share `/app/.next`; the build wipes the dev server's manifests and every page
  then 500s with `ENOENT: /app/.next/routes-manifest.json`. To check a production build, copy
  `frontend/` elsewhere (or use `infrastructure/docker/Dockerfile.frontend.prod`) and build there.
- The backend image is installed with `uv pip install --system -e`; `uvicorn` must run from `/app`
  (`backend.app.main:app`), which the image's `WORKDIR` and `PYTHONPATH` already provide.
- `SECRET_KEY` and other environment values come from `.env.base44-defaults` (committed
  placeholders) and, when the platform supplies them, `/run/base44/app.env` — listed last so the
  dashboard value wins. Local DB/Redis credentials are inline in the compose file on purpose.
- Dev mode still validates `AUTH_ENCRYPTION_KEY` if set (must be a valid Fernet key). Production
  additionally refuses to start without a strong `SECRET_KEY`, `AUTH_ENCRYPTION_KEY`,
  `COOKIE_SECURE=true`, `RESEND_API_KEY` and a non-`@resend.dev` `MAIL_FROM`
  (`Settings.validate_production`). Transactional mail is suppressed in development instead of
  failing, so email verification links never arrive locally.

### Sandbox-only frontend configuration (BASE44_PREVIEW_MODE)

The preview is single-origin: the browser calls `/api/v1/*` on port 3000 and the Next dev server
proxies it to `backend:8000`, keeping session cookies first-party. Both behaviours in
`frontend/next.config.js` are gated on `BASE44_PREVIEW_MODE === "1"` and are inert otherwise:

- `previewApiTarget` (from `API_PROXY_TARGET`) installs the `/api/:path*` rewrite.
- `allowedDevOrigins` (from `BASE44_PUBLIC_HOST_SUFFIX`) lets Next >= 15.5 accept the preview
  origin's requests for dev assets and HMR. Without it the page loads but hydration/assets fail.

Production is unaffected: Caddy routes `/api/*` to the backend, `NEXT_PUBLIC_API_URL` is empty, and
the client uses relative URLs.

## Verifying a change

There is **no test suite in this repository** — `Makefile`/`CLAUDE.md` reference `tests/backend`
and `frontend/src/**/*.test.ts`, but the `tests/` directory and all spec files are absent. `make
test` fails, and `frontend`'s `npm test` is a stub that exits 0.

Verify by exercising the running stack instead:

```bash
curl -s -o /dev/null -w '%{http_code}\n' http://localhost:3000/            # preview serves
curl -s http://localhost:8000/api/health                                    # liveness
curl -s http://localhost:8000/api/ready                                     # 200 only if DB + Redis are live
curl -s -o /dev/null -w '%{http_code}\n' http://localhost:3000/api/health   # same-origin proxy path
```

`/api/ready` (added with the deployment work) returns 503 when PostgreSQL or Redis is unreachable,
so it is the right probe for "did the app really come up".

## Deployment (Vultr)

`docs/DEPLOY_VULTR.md` is the runbook; `infrastructure/vultr/*.sh` and
`infrastructure/vultr/docker-compose.prod.yml` implement it. Validate a change to it without a
Vultr host like this:

```bash
# 1. the compose file must interpolate cleanly (needs POSTGRES_* etc.)
set -a; . /path/to/production.env; set +a
OPENDOMAIN_ENV_FILE=/path/to/production.env \
  docker compose -f infrastructure/vultr/docker-compose.prod.yml config --quiet
# 2. both production images must build
docker build -f infrastructure/docker/Dockerfile.backend.prod -t opendomain-backend:test .
docker build -f infrastructure/docker/Dockerfile.frontend.prod -t opendomain-frontend:test .
```

- The scripts run on Ubuntu/Debian: keep shell utilities portable. `stat -f` is BSD/macOS syntax
  and silently prints filesystem information on GNU coreutils, which once made `deploy.sh` refuse a
  perfectly valid `0600` env file before running any compose command. Use `stat -c` with a
  `stat -f` fallback (see `file_mode` in `deploy.sh`).
- `deploy.sh` sources the env file and exports `OPENDOMAIN_ENV_FILE`, so every compose command it
  runs sees the same configuration; `docker compose ... build --pull` is what actually takes time.
- The production frontend image is built with `NEXT_PUBLIC_API_URL=""`; that value is baked at
  build time, so changing it requires a rebuild (and Caddy owns `/api/*` routing).
