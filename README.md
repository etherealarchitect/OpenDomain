# OpenDomain

**The first Open Source Agentic Domain Registrar**

OpenDomain is a full-stack, open-source domain registrar platform with an integrated AI agent that can execute any platform action through natural language. Register domains, manage DNS, monitor uptime, trade on the marketplace, and more — all from a terminal-inspired interface or a conversational AI assistant.

---

## Features

### Core Registrar
- **Domain Registration & Transfer** — Search, register, renew, and transfer domains with full ICANN lifecycle support
- **DNS Management** — Full CRUD for 14 record types (A, AAAA, CNAME, MX, TXT, NS, SRV, CAA, SOA, PTR, NAPTR, SSHFP, TLSA, LOC) with BIND import/export
- **DNS Templates** — One-click setup for GitHub Pages, Google Workspace, Microsoft 365, Vercel, and Netlify
- **WHOIS Contacts** — Create and manage registrant contacts with privacy protection enabled by default
- **WHOIS Lookup** — Query registration data for any domain
- **DNSSEC** — Enable, disable, and rotate DNSSEC keys with DS record management

### AI Agent
- **21 Tool Definitions** — The agent can search domains, manage DNS, handle billing, configure monitoring, and more
- **Natural Language Interface** — Conversational chat with suggestion chips for common actions
- **Powered by Claude** — Uses Claude via AWS Bedrock with full tool-use capabilities

### Monitoring & Alerts
- **Domain Watch** — Monitor availability of domains you want to acquire
- **Uptime Checks** — HTTP/HTTPS monitoring with configurable intervals
- **SSL Certificate Tracking** — Monitor certificate expiry and chain validity
- **Alert Rules** — Configurable notifications for expiry, downtime, and SSL issues

### Marketplace
- **List Domains for Sale** — Set asking prices for domains you own
- **Browse & Offer** — Discover listed domains and submit purchase offers
- **Offer Management** — Accept, reject, or counter offers

### Billing & Administration
- **Invoices & Transactions** — Full billing history and payment tracking
- **Payment Methods** — Manage stored payment methods
- **API Keys** — Programmatic access with scoped permissions
- **Webhooks** — Subscribe to platform events (domain.registered, dns.updated, etc.)
- **Email Forwarding** — Create forwarding rules including catch-all addresses
- **SSL Certificates** — Request and manage Let's Encrypt certificates
- **Bulk Operations** — Register, renew, lock, or unlock domains in batch

### CLI
- **Full-featured CLI** — `opendomain` command covering all platform operations
- **Command Groups** — domains, dns, contacts, whois, agent, monitoring, webhooks, marketplace, ssl, billing, api-keys, bulk

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.12+ / FastAPI / SQLAlchemy (async) / Alembic |
| Frontend | Next.js 15 / TypeScript / Tailwind CSS v4 / React Query / Zustand |
| Database | PostgreSQL 16 + Redis |
| DNS | PowerDNS integration + native zone management |
| EPP | Async EPP client (RFC 5730-5734) with simulation mode |
| AI | Claude via AWS Bedrock with 21 tool definitions |
| Auth | JWT with bcrypt password hashing |
| Infrastructure | Docker Compose |

---

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Node.js 22+ (for local frontend development)
- Python 3.12+ (for local backend development)

### Run with Docker Compose

```bash
git clone https://github.com/etherealarchitect/OpenDomain.git
cd OpenDomain
cp .env.example .env   # Configure your environment variables
make dev
```

The platform will be available at:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### Run Individually

```bash
# Backend only
make backend

# Frontend only
make frontend

# Database migrations
make migrate

# Create a new migration
make migrate-create msg="add new table"
```

### Run Tests

```bash
make test           # All tests
make test-backend   # Backend only
make test-frontend  # Frontend only
```

---

## Project Structure

```
backend/                   Python FastAPI backend
  app/
    api/routes/            14 REST endpoint modules (50+ endpoints)
    models/                12 SQLAlchemy ORM models
    schemas/               Pydantic request/response schemas
    services/              Business logic layer
      epp/                 Async EPP protocol client
      dns/                 DNS management service
    agent/                 AI agent with 21 platform tools
    core/                  Config, security, database setup
    middleware/            Request middleware
    cli.py                 CLI entry point
  migrations/              Alembic database migrations

frontend/                  Next.js 15 frontend
  src/
    app/                   17 pages via App Router
    components/            Reusable React components
    lib/                   API client (~80 methods), utilities
    hooks/                 Custom React hooks
    types/                 TypeScript type definitions

infrastructure/            Docker, deployment configs
  docker/                  Development & production Dockerfiles
scripts/                   Dev and deployment scripts
tests/                     Backend and frontend test suites
```

---

## API Overview

All endpoints are under `/api/v1`. Authentication is via JWT Bearer token.

| Module | Endpoints | Description |
|--------|-----------|-------------|
| Auth | 3 | Register, login, profile |
| Domains | 6 | CRUD, search, renew, transfer |
| DNS | 5 | Records, zones, templates, BIND export |
| Contacts | 4 | WHOIS contact management |
| WHOIS | 1 | Domain WHOIS/RDAP lookup |
| Agent | 1 | AI chat with tool execution |
| Monitoring | 12 | Watches, uptime, SSL monitors, alerts |
| Marketplace | 9 | Listings, offers, browse |
| Billing | 8 | Invoices, transactions, payment methods |
| Webhooks | 4 | Event subscription management |
| Email Forwards | 4 | Forwarding rules per domain |
| SSL | 5 | Certificate lifecycle |
| Bulk | 5 | Batch domain operations |
| API Keys | 3 | Programmatic access tokens |

Interactive API documentation is available at `/docs` (Swagger UI) when the backend is running.

---

## Configuration

Key environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql+asyncpg://opendomain:opendomain@localhost:5432/opendomain` |
| `REDIS_URL` | Redis connection string | `redis://localhost:6379/0` |
| `JWT_SECRET` | Secret key for JWT signing | (required) |
| `EPP_HOST` | EPP server hostname | `localhost` |
| `EPP_PORT` | EPP server port | `700` |
| `EPP_SIMULATE` | Run EPP in simulation mode | `true` |
| `AWS_REGION` | AWS region for Bedrock | `ap-southeast-2` |
| `ANTHROPIC_MODEL` | Claude model ID | `anthropic.claude-fable-5` |
| `NEXT_PUBLIC_API_URL` | Backend URL for frontend | `http://localhost:8000` |

---

## CLI Usage

```bash
# Install the CLI
pip install -e backend/

# Domain operations
opendomain domains list
opendomain domains search example.com
opendomain domains register example.com --contact-id <uuid>

# DNS management
opendomain dns list example.com
opendomain dns add example.com A www 1.2.3.4

# AI agent
opendomain agent chat "Register example.com with my default contact"

# Monitoring
opendomain monitoring alerts
opendomain monitoring watch example.com
opendomain monitoring uptime-add https://example.com

# Marketplace
opendomain marketplace browse
opendomain marketplace create example.com --price 5000

# Full help
opendomain --help
```

---

## Design

OpenDomain uses a terminal-inspired dark theme with a custom design token system:

| Token | Purpose |
|-------|---------|
| `ground` | Background surfaces |
| `ink` | Text and content |
| `edge` | Borders and dividers |
| `focus` | Primary actions and links |
| `live` | Success states |
| `caution` | Warning states |
| `fault` | Error states |

Typography: **Inter** for UI, **JetBrains Mono** for code and data.

---

## Development

### EPP Simulation Mode

By default, OpenDomain runs with `EPP_SIMULATE=true`, which simulates all registry operations locally. This allows full development and testing without connecting to a live EPP server. Disable simulation mode and configure EPP credentials when connecting to a real registry.

### AI Agent Development

The agent uses Claude's tool-use API with 21 defined tools. Each tool maps to a backend service method. To add a new tool:

1. Define the tool schema in `backend/app/agent/tools.py`
2. Add the handler method in `backend/app/agent/agent.py`
3. Wire it to the appropriate service in `backend/app/services/`

---

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## License

This project is open source. See the [LICENSE](LICENSE) file for details.

---

## Links

- **Repository**: [github.com/etherealarchitect/OpenDomain](https://github.com/etherealarchitect/OpenDomain)
- **Issues**: [github.com/etherealarchitect/OpenDomain/issues](https://github.com/etherealarchitect/OpenDomain/issues)

---

<p align="center">
  <strong>&lt;.&gt; opendomain</strong><br/>
  <em>The first Open Source Agentic Domain Registrar</em>
</p>
