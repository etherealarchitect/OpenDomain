# OpenDomain — Base44 dev environment

Full-stack registrar: FastAPI backend + Next.js 15 frontend + PostgreSQL 16 + Redis.
The sandbox stack is defined in `docker-compose.base44.yml`; the repository's own
`docker-compose.yml` / `infrastructure/docker/*.prod` images are for real
deployments and are not used here.

## Running

```bash
docker compose -f docker-compose.base44.yml up -d --build
```

- Frontend (Next.js dev server, live reload) is the public entry point on **host port 3000**.
- Backend (uvicorn `--reload`) is also published on **host port 8000**; API docs at `/docs`, health probes at `/api/health` (liveness) and `/api/ready` (database + Redis).
- Logs: `docker compose -f docker-compose.base44.yml logs -f backend|frontend`.

## What is non-obvious

- **Single origin.** The browser only calls port 3000. `frontend/next.config.js` rewrites `/api/:path*` to `API_PROXY_TARGET` (`http://backend:8000`), a server-side-only variable, so the `HttpOnly` session cookie stays first-party. `NEXT_PUBLIC_API_URL` is deliberately empty — do not point it at the backend origin, or browser calls become cross-site and break cookie auth.
- **Python dependencies are installed at container start**, not baked into an image: each Python service runs `pip install uv` then `uv pip install --system -e '.[dev]'` from `/app/backend`. The repo is bind-mounted at `/app`, so edits need no rebuild; a compose/env/dependency change does (`--build` and `up -d`).
- **Migrations run in a one-shot `migrate` service** (`alembic upgrade head`), and the backend waits for `service_completed_successfully`. Alembic must be run from `/app/backend` (its `script_location` is relative to the working directory); `PYTHONPATH=/app` makes `backend.app` importable.
- **Secrets.** `.env.base44-defaults` holds committed development placeholders and is listed before `/run/base44/app.env`, so dashboard secrets override it. No external credential is required to boot: EPP is simulated, and email (Resend) plus the Bedrock-backed AI agent degrade gracefully when their keys are absent. Email is suppressed in development, so verification links are **not** delivered — an email-verification signup cannot be completed end to end in the sandbox.
- **Dev origin gating.** `allowedDevOrigins` in `frontend/next.config.js` is derived from `BASE44_PUBLIC_HOST_SUFFIX` and only applied when `BASE44_PREVIEW_MODE === "1"`; both are passed into the frontend service's environment. Without it Next.js blocks preview requests for dev assets/HMR.
- **PowerDNS is not started** by the sandbox stack. `POWERDNS_API_URL`/`POWERDNS_API_KEY` still have config defaults, but nothing in `backend/app` makes HTTP calls to PowerDNS — DNS zones and records are managed in the application database (`backend/app/services/dns_service.py`).
- **Tests run inside the services** (the sandbox host has no Python or Node):
  ```bash
  docker compose -f docker-compose.base44.yml exec -T backend sh -c "cd /app/backend && pytest ../tests/backend -x -q"
  docker compose -f docker-compose.base44.yml exec -T frontend npm test
  ```
  Lint/type-check: `docker compose -f docker-compose.base44.yml exec -T backend sh -c "cd /app/backend && ruff check . && mypy app/"`. The frontend `test` script is still the `echo` placeholder from `package.json`.
- **Verifying the served frontend is live source**, not a prebuilt bundle: `curl -s http://localhost:3000/ | grep -c 'next/dist/client'`-style dev output plus the presence of `_next/static/chunks` HMR scripts; `docker compose ... logs frontend` shows per-route compilation instead of a production start.
