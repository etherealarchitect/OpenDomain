# Deploy OpenDomain on Vultr

This runbook deploys the **application platform** to a single Vultr Cloud Compute instance. It does not turn OpenDomain into an accredited, live registrar. Keep `EPP_SIMULATE=true` until registry credentials, certificates, allowlisting, compliance, and end-to-end registry testing are complete. Likewise, do not offer public authoritative DNS or certificate issuance until PowerDNS synchronization, nameserver delegation, ACME issuance, and background workers are implemented and tested.

## Safety requirements

- Treat any cloud API key pasted into chat, source, terminal output, or issue tracker as compromised. Revoke it, review account activity, and create a replacement with the narrowest permissions necessary.
- Keep the Fly deployment online during setup, DNS propagation, and at least 24–48 hours of observation after cutover.
- Do not commit `/opt/opendomain/.env`, private keys, database dumps, or generated credentials.
- Perform this procedure with a dedicated deploy user and SSH key; disable SSH password authentication.

## Architecture

```text
Internet
  │  TCP 80/443
  ▼
Caddy ── / ───────► Next.js frontend
  │
  └── /api/* ─────► FastAPI backend ──► PostgreSQL / Redis
                                      (private Docker network only)
```

The browser and API share `https://app.example.com`. This permits a host-only `HttpOnly`, `Secure`, `SameSite=Lax` session cookie and avoids cross-origin cookie configuration. Caddy, not Next.js, owns production `/api/*` routing.

## 1. Prepare Vultr

Create a 2 vCPU / 4 GB RAM (or larger after load testing) Ubuntu or Debian instance in the preferred region. It is a low-traffic launch baseline; assess actual pricing in the Vultr dashboard before creating resources.

Create a Vultr Firewall before exposing the instance:

| Protocol | Port | Source |
| --- | --- | --- |
| TCP | 22 | Operator’s fixed administrative IP only |
| TCP | 80 | Internet |
| TCP | 443 | Internet |

Do **not** allow public access to 3000, 5432, 6379, 8000, 8081, or 2019. Do not enable UDP/TCP 53 unless authoritative DNS is specifically implemented and reviewed.

On the server, apply operating system updates, install Docker Engine and the Compose plugin from Docker’s official instructions, enable unattended security updates, and create `/opt/opendomain` with a non-root deployment user.

## 2. Configure DNS and mail

Before starting Caddy, create an `A` record for a dedicated application hostname such as `app.example.com` to the VM IPv4 address. Use a short migration TTL (for example, 300 seconds). Add an `AAAA` record only when IPv6 is configured and verified.

In Resend, verify the sending domain and publish Resend’s required SPF/DKIM DNS records. Choose a verified sender such as `OpenDomain <no-reply@example.com>`.

## 3. Install application and secrets

```bash
sudo -u opendomain git clone https://github.com/etherealarchitect/OpenDomain.git /opt/opendomain/app
sudo install -d -o opendomain -g opendomain -m 700 /opt/opendomain
sudo -u opendomain cp /opt/opendomain/app/infrastructure/vultr/.env.production.example /opt/opendomain/.env
sudo chmod 600 /opt/opendomain/.env
```

Populate the root/deploy-user-owned `/opt/opendomain/.env`. At a minimum set:

- `OPENDOMAIN_HOSTNAME` and `CADDY_EMAIL`
- `ENVIRONMENT=production`, `APP_URL`, `API_URL`, and exact `CORS_ORIGINS`
- `SECRET_KEY`, `AUTH_ENCRYPTION_KEY`, and `TOKEN_PEPPER` with distinct random values
- `POSTGRES_USER`, a unique `POSTGRES_PASSWORD`, and `POSTGRES_DB`
- `RESEND_API_KEY` and a verified `MAIL_FROM`
- `COOKIE_SECURE=true` and an empty `COOKIE_DOMAIN`
- `EPP_SIMULATE=true`

Generate values locally without printing them into shared logs, for example:

```bash
openssl rand -base64 48
python3 -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())'
```

The backend refuses to start in production without the required encryption key, secure-cookie setting, Resend key, and verified sender.

## 4. Deploy a reviewed revision

The deploy script checks the secret-file permissions, checks out an immutable Git ref, validates Compose interpolation, builds the images, starts private data services, runs migrations, then brings up the application stack.

```bash
cd /opt/opendomain/app
chmod 700 infrastructure/vultr/{deploy,backup,restore}.sh
infrastructure/vultr/deploy.sh 3800be1
```

Use the final reviewed commit SHA rather than a mutable branch name. The stack has no public database, Redis, backend, or frontend ports. Only Caddy publishes ports 80 and 443.

## 5. Verify before cutover

Confirm the following through the temporary hostname or a controlled hosts-file mapping:

1. `https://app.example.com/api/health` returns 200.
2. `https://app.example.com/api/ready` returns 200 only when PostgreSQL and Redis are reachable.
3. HTTP redirects to HTTPS and Caddy has a valid certificate.
4. Registering an account delivers an actual Resend verification email.
5. Email verification, TOTP enrollment, recovery-code confirmation, login, logout, and password reset work.
6. Browser cookies are `HttpOnly`, `Secure`, host-only, and `SameSite=Lax`.
7. Rate limiting works and a Redis failure makes readiness/auth unavailable rather than disabling throttling.
8. Containers and persisted data survive a `docker compose restart`.
9. `docker compose -f infrastructure/vultr/docker-compose.prod.yml ps` shows healthy dependencies.
10. No passwords, mail tokens, session values, or API secrets appear in logs.

Only after these checks pass should the canonical production hostname be pointed to Vultr. Keep Fly active throughout the DNS-cache window and observe logs, memory, disk capacity, database connections, Redis, TLS, and email delivery for 24–48 hours.

## Backup and restore

Run daily backups from a privileged scheduled task. A snapshot alone is not a database recovery strategy.

```bash
/opt/opendomain/app/infrastructure/vultr/backup.sh
```

Set `BACKUP_DESTINATION` to a protected mounted off-host location. The script creates PostgreSQL custom-format dumps, retains 14 days by default, and does not encrypt the destination for you. Configure encryption and access controls at the storage layer, then test a restore under a temporary hostname before relying on it.

`restore.sh` stops public app containers and demands the literal `RESTORE` confirmation before replacing database contents:

```bash
/opt/opendomain/app/infrastructure/vultr/restore.sh /var/backups/opendomain/opendomain-YYYYMMDDTHHMMSSZ.dump
```

## Rollback

If Vultr fails after DNS cutover:

1. Stop or isolate Vultr writes to avoid data divergence.
2. Repoint DNS to the still-running Fly deployment.
3. Leave the Fly database unchanged unless a deliberate data migration was performed.
4. Diagnose and redeploy Vultr under the temporary hostname.
5. Restore from a tested backup only when required.

DNS rollback is subject to resolver caching even with a low TTL. Do not delete Fly resources during the observation period.

## Kimi K3 / GPU follow-up

Do not allocate a permanent GPU as part of this launch. A dedicated GPU instance incurs hourly infrastructure charges while allocated even when it processes no requests. Once application traffic is measured, evaluate Kimi K3 model availability, licensing, VRAM, provider region, egress, and hourly price. Prefer a separate on-demand or auto-stopped worker with a strict spend cap within the $250 overall budget.
