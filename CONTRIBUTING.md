# Contributing to OpenDomain

Thanks for improving OpenDomain. This repository is designed to be safely forked and run locally with simulated registrar behavior.

## Before opening a pull request

1. Fork the repository and work in a feature branch.
2. Copy `.env.example` to `.env`; do not commit the filled-in file.
3. Never add API keys, sessions, registry auth codes, customer data, private keys, certificate files, or backups to commits, issues, tests, or screenshots.
4. Use clearly fake values such as `example.com` in documentation and fixtures.
5. Run the relevant checks before submitting changes:

   ```bash
   make lint
   make test
   cd frontend && npm run build
   ```

6. Update tests, OpenAPI descriptions, and documentation for public API changes.

## Development boundaries

- `EPP_SIMULATE=true` is the default. Do not claim simulated operations create, transfer, or control real domains.
- Keep payment, registrar, PowerDNS, and cloud credentials out of source control. Live-provider work must use test/sandbox credentials supplied through a local secret manager.
- Treat domains, contacts, billing records, transfers, DNS zones, API keys, and webhooks as tenant-bound resources. New endpoints must enforce ownership checks and avoid revealing whether another tenant’s resource exists.
- External state changes need idempotency, audit trails, provider error handling, and tests for retry/reconciliation.

## Pull-request expectations

Describe the user-visible behavior, security/privacy impact, tests run, migration impact, documentation changes, and any provider configuration needed. Keep commits focused. Do not submit generated build artifacts unless the release workflow explicitly requires them.

## Reporting security issues

See [SECURITY.md](SECURITY.md). Please use private disclosure rather than public issues for vulnerabilities.
