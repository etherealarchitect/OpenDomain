# Security Policy

## Supported versions

Security fixes are developed on the latest `main` branch. Until the project publishes stable releases, run the latest reviewed commit and keep all provider integrations disabled unless explicitly configured for a sandbox.

## Report a vulnerability

**Do not open a public GitHub issue for a suspected vulnerability.**

Use the repository owner’s configured **private vulnerability reporting** channel on GitHub, if enabled. If private reporting is not enabled, contact the maintainers through a verified private channel listed in the repository settings. Do not use a public issue for a suspected vulnerability.

Include:

- a clear description and potential impact;
- reproducible steps or a proof of concept that avoids accessing other users’ data;
- affected commit, endpoint, or component;
- any proposed mitigation.

Please do not include passwords, API keys, session values, payment data, registry auth codes, private keys, or personally identifiable customer data. If a credential was exposed, revoke it immediately and state only its provider/type in the report.

Please allow maintainers reasonable time to assess and remediate a report before public disclosure. Any acknowledgement, timeline, or disclosure coordination will depend on maintainer capacity and the reporting channel.

## Production-integrations policy

OpenDomain defaults to simulated registrar behavior. Live registrar, payment, authoritative-DNS, and certificate-issuance integrations require separately reviewed credentials, provider approval, tenant isolation, audit logging, incident response, and a deployment-specific production gate. Never enable these integrations based solely on code availability.

## Secure configuration

- Do not commit `.env` files, provider credentials, certificates, backups, or generated CLI sessions.
- Use a secret manager or root-owned deployment environment file with mode `0600`.
- Store CLI session state in the XDG state directory (or an explicitly private `OPENDOMAIN_STATE_DIR`), never in a repository.
- Rotate any credential that appears in source control, chat, logs, CI output, or public issues.
