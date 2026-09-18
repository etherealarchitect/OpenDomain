# OpenDomain — Base44 dev environment

## Running the app

```
docker compose -f docker-compose.base44.yml up -d
```

- Frontend (Next.js 15 dev, live reload) is the **single public origin** on host port 3000.
- Backend (FastAPI / uvicorn `--reload`) runs on internal port 8000 and is **not** exposed to the host.
- The Next.js dev server proxies `/api/*` to the backend over the Docker network (`BACKEND_INTERNAL_URL=http://backend:8000`), so browser cookie/session auth stays same-origin. Do **not** set `NEXT_PUBLIC_API_URL` to the backend origin — the browser must call same-origin `/api`.
- PostgreSQL 16 and Redis 7 run as compose services with healthchecks.

## First-boot behavior

- The backend container installs Python deps with `uv`, runs `alembic upgrade head`, then starts uvicorn. Migrations run on every backend start (idempotent).
- The frontend container runs `npm install` then `next dev -H 0.0.0.0`. `node_modules` lives in a named volume so host bind-mount doesn't clobber it.

## Secrets

No external secrets are required to boot in `ENVIRONMENT=development` (EPP is simulated, email/AI are optional). `.env.base44-defaults` holds dev placeholders; real values delivered to `/run/base44/app.env` override them. Add production secrets (SECRET_KEY, AUTH_ENCRYPTION_KEY, RESEND_API_KEY, AWS Bedrock creds) via the dashboard before production use.

## Preview origin

`next.config.js` adds `allowedDevOrigins` from `BASE44_PUBLIC_HOST_SUFFIX` so the preview origin can fetch dev assets/HMR. The var is passed into the frontend service's `environment`.

## Repo layout

- `backend/` — FastAPI app (import root is the repo root: `backend.app.main:app`). Alembic config at `backend/alembic.ini`.
- `frontend/` — Next.js App Router (17 pages). API client at `frontend/src/lib/api.ts` uses `credentials: "include"` with same-origin base.
- `infrastructure/` — production Dockerfiles / Caddy / Vultr configs (not used by the Base44 dev compose).
