# OpenDomain

Open-source domain registrar platform with integrated AI agent.

## Architecture

- **Backend**: Python 3.12+ / FastAPI / SQLAlchemy (async) / Alembic
- **Frontend**: Next.js 15 / TypeScript / Tailwind CSS
- **Database**: PostgreSQL 16 + Redis
- **DNS**: PowerDNS integration + native zone management
- **AI Agent**: Claude-powered agent with tool-use for all platform actions
- **EPP**: Async EPP client for registry communication (RFC 5730-5734)
- **Infrastructure**: Docker Compose for local deployment

## Project Structure

```
backend/           Python FastAPI backend
  app/
    api/routes/    REST endpoints
    models/        SQLAlchemy ORM models
    schemas/       Pydantic request/response schemas
    services/      Business logic layer
      epp/         EPP protocol client
      dns/         DNS management service
    agent/         AI agent with platform tools
    core/          Config, security, database
    middleware/    Request middleware
  migrations/      Alembic DB migrations

frontend/          Next.js frontend
  src/
    app/           App router pages
    components/    React components
    lib/           Utilities and API client
    hooks/         Custom React hooks
    types/         TypeScript type definitions

infrastructure/    Docker, nginx, DNS configs
scripts/           Dev and deployment scripts
tests/             Backend and frontend tests
```

## Commands

```bash
make dev          # Start full stack locally (docker-compose)
make backend      # Start backend only
make frontend     # Start frontend only
make migrate      # Run database migrations
make test         # Run all tests
make lint         # Lint all code
```

## Key Design Decisions

- EPP client is async (asyncio) for non-blocking registry communication
- DNS zones stored in PostgreSQL, synced to PowerDNS via API or native backend
- AI agent uses Claude tool-use to execute any platform action the user describes
- All prices in minor currency units (cents) to avoid floating point
- Domain lifecycle follows ICANN standards (pendingCreate, active, pendingTransfer, etc.)
- WHOIS privacy is on by default
- The platform can run fully local with simulated EPP for development
