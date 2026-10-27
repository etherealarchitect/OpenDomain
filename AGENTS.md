# AGENTS.md — running OpenDomain in the Base44 sandbox

Python/FastAPI + Next.js monorepo. The notes below are only the non-obvious things
learned while wiring it up here; manifests and the README cover the rest.

## Run it

```bash
docker compose -f docker-compose.base44.yml up -d --build   # full stack
docker compose -f docker-compose.base44.yml ps -a           # health + one-shot status
docker compose -f docker-compose.base44.yml logs -f backend
```

- Web entry point: **http://localhost:3000** (Next.js dev server, bind-mounted source).
- API: http://localhost:8000, interactive docs at http://localhost:8000/docs.
- Do **not** use the repository's own `docker-compose.yml` in the sandbox: those images
  bake the source in, so edits would never show up.

## Architecture facts that affect running it

- **Single origin.** Only port 3000 is user-facing. The backend session cookie is
  `SameSite=Lax` (`backend/app/api/routes/auth.py`), so a cross-origin API call could
  never send it; the Next.js dev server therefore proxies `/api/*` to the `backend`
  container and the frontend runs with `NEXT_PUBLIC_API_URL` unset, so
  `frontend/src/lib/api.ts` uses relative URLs.
- **Migrations** run as the one-shot `migrate` service and the backend waits for it
  (`service_completed_successfully`). Alembic reads `DATABASE_URL` through the app
  settings (`backend/migrations/env.py`), so that service needs the variable too —
  the hardcoded `sqlalchemy.url` in `alembic.ini` is ignored.
- **Health/readiness probes already exist**: `GET /api/health` (process) and
  `GET /api/ready` (PostgreSQL + Redis). Compose healthchecks use the first one.
- **Redis** is required for `/api/ready` and for auth rate limiting.
- **PowerDNS** appears in the repo's own compose and in `backend/app/core/config.py`,
  but no application code reads `POWERDNS_API_URL` yet, so it is deliberately not part
  of the sandbox stack.
- **No `tests/` directory exists on this branch** although the Makefile and README
  reference `../tests/backend`; `make test` fails until that suite lands.
- `backend/opendomain.egg-info/`, `frontend/node_modules/` and `frontend/.next/` are
  created inside the repo directory by the containers; all three are gitignored.

## Sandbox-only overrides

`frontend/next.config.js` has two overrides gated on `BASE44_PREVIEW_MODE === "1"`
(the platform sets that variable to `1` for sandbox commands):

| Override | Why |
| --- | --- |
| `allowedDevOrigins: ["3000-<BASE44_PUBLIC_HOST_SUFFIX>"]` | The preview reaches the dev server through a proxy; without this Next.js blocks dev assets and HMR. |
| `/api/:path*` rewrite to `API_PROXY_TARGET` | Keeps API calls same-origin so the `SameSite=Lax` session cookie is sent. |
| `skipTrailingSlashRedirect: true`, plus a `/api/:path*/` rewrite ahead of `/api/:path*` | Several API paths end in a slash (`/whois/`, `/contacts/`, `/domains/`, `/domains/{id}/dns/`, `/webhooks/`, `/api-keys/`). Next.js would 308 them to the slash-less path, FastAPI would then answer 307 with an absolute `http://backend:8000/...` URL, and the browser cannot resolve that host — the call fails. Production is unaffected because Caddy sends `/api` straight to FastAPI. A hand-written request to a slash-less API path still sees that 307: call the trailing-slash form FastAPI declares. |

`docker-compose.base44.yml` passes `BASE44_PREVIEW_MODE`, `BASE44_PUBLIC_HOST_SUFFIX`
and `API_PROXY_TARGET` in; no resolved host value is hardcoded anywhere. With the flag
unset, both overrides are disabled and Next.js behaves exactly as before.

The backend's `APP_URL`/`API_URL`/`CORS_ORIGINS` are derived from
`${BASE44_PUBLIC_HOST_SUFFIX}` in the compose file for the same reason: `APP_URL` is
what verification/reset links are built from, and `CORS_ORIGINS` must cover the
preview origin.

## Secrets

- `SECRET_KEY` arrives from the platform at `/run/base44/app.env`, loaded **after**
  `.env.base44-defaults` so a dashboard value always wins. The defaults file carries
  only a 32+ character development placeholder.
- `AUTH_ENCRYPTION_KEY` and `TOKEN_PEPPER` are left unset: the backend derives both
  from `SECRET_KEY` when absent (`backend/app/core/config.py`).
- Optional integrations needing real credentials: `RESEND_API_KEY` (transactional
  email) and `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` (AI agent via Bedrock).
  Without `RESEND_API_KEY` development suppresses delivery, so **email verification
  cannot be completed and no account can reach the signed-in screens**; the agent page
  fails without the Bedrock credentials. EPP runs simulated (`EPP_SIMULATE=true`), so
  no registry credentials are needed.

## Known quirks

- Frontend dependencies install with `npm ci` on container start. Keep it that way:
  with the source bind-mounted, `npm install` (npm 10) rewrites
  `frontend/package-lock.json`, dirtying the working tree. `npm ci` only reads it.
- Next.js compiles routes on demand, so the first request to an unvisited route takes
  a few seconds. A route that looks like it does not render right after a fresh start
  is usually still compiling — request it once before diagnosing a routing bug.
- The backend image installs dependencies at build time (editable, from
  `backend/pyproject.toml`); after a dependency change, rebuild with
  `docker compose -f docker-compose.base44.yml up -d --build backend`.
- `bcrypt` is pinned to `<4.1` in `backend/pyproject.toml`. passlib 1.7.4 is
  unmaintained and cannot drive bcrypt >= 4.1 (it reads `bcrypt.__about__`, and
  bcrypt 5.0 rejects passlib's over-length probe password), which makes **every**
  `hash_password`/`verify_password` call raise — registration and sign-in fail with
  a 500. Do not raise the pin without replacing passlib.

## Verifying a change

- Frontend edits hot-reload through the bind mount (`./frontend` → `/app`).
- Backend edits hot-reload through `uvicorn --reload` (`./backend` → `/app/backend`);
  if a change is not picked up, `docker compose -f docker-compose.base44.yml restart backend`.
- Compose/config/dependency/env changes need another `up -d --build`, then a preview reload.
- Checks run inside the containers, e.g.
  `docker compose -f docker-compose.base44.yml exec -T backend ruff check backend`.
