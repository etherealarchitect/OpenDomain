# AGENTS.md — running OpenDomain in the Base44 sandbox

This repository is a Python/FastAPI + Next.js monorepo. The notes below are the
non-obvious things discovered while wiring it up here; manifests and the README
describe the rest.

## Running it

```bash
docker compose -f docker-compose.base44.yml up -d --build   # full stack
docker compose -f docker-compose.base44.yml ps -a           # health + one-shot status
docker compose -f docker-compose.base44.yml logs -f backend
```

- Web entry point: **http://localhost:3000** (Next.js dev server, bind-mounted source).
- API: http://localhost:8000 and docs at http://localhost:8000/docs.
- Do **not** use the repository's own `docker-compose.yml` for development in the
  sandbox: those images bake the source in, so edits would not show up.

## Architecture notes that affect running it

- **Single origin.** The browser must only ever talk to port 3000. The backend
  session cookie is `SameSite=Lax` (`backend/app/api/routes/auth.py`), so a
  cross-origin API call could never send it. The Next.js dev server therefore
  proxies `/api/*` to the `backend` container, and the frontend runs with
  `NEXT_PUBLIC_API_URL` unset so `frontend/src/lib/api.ts` uses relative URLs.
- **Migrations** run as the one-shot `migrate` service before the API starts; the
  backend waits for it (`service_completed_successfully`). Alembic reads
  `DATABASE_URL` from the app settings, so that service needs the variable too —
  without it Alembic silently falls back to `localhost:5432` and fails.
- **Health/readiness probes already exist**: `GET /api/health` (process) and
  `GET /api/ready` (PostgreSQL + Redis). Compose healthchecks use them.
- **Redis** is required for `/api/ready` and for auth rate limiting outside tests.
- **PowerDNS** is configured in the repo's own compose but no code references
  `POWERDNS_API_URL`/`dns_provider` yet, so it is intentionally not part of the
  sandbox stack. DNS zones are application-managed for now.
- **No `tests/` directory exists on this branch** although the Makefile references
  `../tests/backend`. `make test` fails until that suite lands; the branch may
  predate it.

## Sandbox-only overrides

`frontend/next.config.js` contains two overrides gated on `BASE44_PREVIEW_MODE === "1"`
(the platform sets that variable to `1` for sandbox commands):

| Override | Why |
| --- | --- |
| `allowedDevOrigins: ["3000-<BASE44_PUBLIC_HOST_SUFFIX>"]` | The preview reaches the dev server through a proxy, so its origin must be allow-listed or Next.js blocks dev assets and HMR. |
| `/api/:path*` rewrite to `API_PROXY_TARGET` | Keeps API calls same-origin so the `SameSite=Lax` session cookie is sent (see above). |

- When `BASE44_PREVIEW_MODE` is unset (or any value other than `1`), both are
  disabled and Next.js behaves exactly as before (rewrites only when
  `NEXT_PUBLIC_API_URL` is an explicit backend origin).
- `BASE44_PUBLIC_HOST_SUFFIX`, `BASE44_PREVIEW_MODE` and `API_PROXY_TARGET` are
  passed in by `docker-compose.base44.yml`; no resolved host value is ever
  hardcoded.

## Secrets

- `SECRET_KEY` arrives from the platform at `/run/base44/app.env`, which compose
  loads **after** `.env.base44-defaults` so a dashboard value always wins. The
  defaults file only carries a 32+ character development placeholder.
- `AUTH_ENCRYPTION_KEY` and `TOKEN_PEPPER` are left unset: the backend derives both
  from `SECRET_KEY` when they are absent.
- Optional integrations that need real credentials: `RESEND_API_KEY` (transactional
  email — without it development suppresses delivery and only logs that an email was
  requested, so email verification cannot be completed) and `AWS_ACCESS_KEY_ID` /
  `AWS_SECRET_ACCESS_KEY` (AI agent via AWS Bedrock; the agent page fails without
  them). EPP runs in simulation mode (`EPP_SIMULATE=true`), so no registry
  credentials are needed.

## Known quirks

- Frontend dependencies install with `npm ci` on container start. Keep it that way:
  with the source bind-mounted, `npm install` (npm 10) rewrites
  `frontend/package-lock.json` (it strips `libc` fields from the lock), which dirties
  the working tree. `npm ci` only ever reads the committed lockfile.
- Next.js compiles routes on demand, so the **first** request to a route that has not
  been visited yet takes a few seconds. A route that appears "not to render" right
  after a fresh start is usually still compiling — request it once (or wait) before
  diagnosing a routing bug.
- `backend/opendomain.egg-info/` and `frontend/node_modules/`, `frontend/.next/` are
  created inside the repo directory by the containers; all three are gitignored.

## Verifying a change

- Frontend edits hot-reload through the bind mount (`./frontend` → `/app`).
- Backend edits hot-reload through `uvicorn --reload` (`./backend` → `/app/backend`).
  If a change is not picked up, `docker compose -f docker-compose.base44.yml restart backend`.
- Compose/config, dependency and env changes need a `up -d --build` run.
- Backend checks run inside the container, e.g.
  `docker compose -f docker-compose.base44.yml exec -T backend python -m pytest`
  or `... exec -T backend ruff check backend`.
