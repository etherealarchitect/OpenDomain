# OpenDomain — Base44 Dev Environment

## Overview
Full-stack domain registrar: FastAPI backend + Next.js 15 frontend + PostgreSQL 16 + Redis + PowerDNS.

## Running
```bash
docker compose -f docker-compose.base44.yml up -d
```
- Frontend: http://localhost:3000 (Next.js dev server with live reload)
- Backend API: http://localhost:8000 (uvicorn --reload)
- API docs: http://localhost:8000/docs

## Architecture Notes
- **Single-origin setup**: The Next.js dev server proxies `/api/*` to the backend via `next.config.js` rewrites using the `API_ORIGIN` env var (server-side only). The browser talks to port 3000 only, so cookie-based auth (SameSite=Lax, HttpOnly) works without cross-origin CORS complications.
- `NEXT_PUBLIC_API_URL` is intentionally **not set** — the frontend API client defaults to same-origin (`""`), and requests are proxied by the Next.js rewrite.
- `allowedDevOrigins` in `next.config.js` is derived from `BASE44_PUBLIC_HOST_SUFFIX` so the preview origin can access Next.js dev assets/HMR.

## Services (docker-compose.base44.yml)
- **db** — postgres:16-alpine (user/pass/db: opendomain)
- **redis** — redis:7-alpine
- **powerdns** — pdns-auth-49 with gpgsql backend (API key: change-me)
- **backend** — python:3.12-slim, bind-mounts repo at /app, installs deps + runs alembic migrations + uvicorn --reload
- **frontend** — node:22-alpine, bind-mounts frontend, npm install + next dev

## No external secrets required for dev
The app boots in development mode with built-in defaults:
- `SECRET_KEY` is set to a dev placeholder (fine for non-production)
- `AUTH_ENCRYPTION_KEY` is derived from SECRET_KEY at runtime
- `EPP_SIMULATE=true` — no real registry connection
- `RESEND_API_KEY` — optional (email sending disabled without it)
- `AWS_ACCESS_KEY_ID`/`AWS_SECRET_ACCESS_KEY` — optional (AI agent disabled without them)

## Migrations
Alembic migrations run automatically on backend startup. Two revisions exist:
- 20260911_0001: initial schema
- 20260911_0002: secure auth lifecycle tables

## Key Commands
```bash
docker compose -f docker-compose.base44.yml logs -f backend   # tail backend logs
docker compose -f docker-compose.base44.yml logs -f frontend  # tail frontend logs
docker compose -f docker-compose.base44.yml exec db psql -U opendomain -d opendomain  # DB shell
```
