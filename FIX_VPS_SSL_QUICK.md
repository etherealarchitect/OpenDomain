# Quick Fix: SSL Certificate for VPS

## Problem
HTTPS to https://opendomain.etherealcode.org fails with TLS error.

## Root Cause
Caddyfile has wrong domain: `opendomain.scottkbrown.com` instead of `opendomain.etherealcode.org`

## Fix Commands (SSH to VPS)

```bash
# 1. SSH to VPS (use your credentials)
ssh username@108.61.169.174

# 2. Update Caddyfile
cd /opt/opendomain/app
sed -i 's/opendomain\.scottkbrown\.com/opendomain.etherealcode.org/g' infrastructure/vultr/Caddyfile

# 3. Restart Caddy
docker compose --env-file /opt/opendomain/.env -f infrastructure/vultr/docker-compose.prod.yml restart caddy

# 4. Check logs
docker compose --env-file /opt/opendomain/.env -f infrastructure/vultr/docker-compose.prod.yml logs --tail=10 caddy

# 5. Test (wait 1 minute)
curl -I https://opendomain.etherealcode.org
```

## Verify DNS
```
dig +short opendomain.etherealcode.org
# Should return: 108.61.169.174
```

## Full documentation
See `docs/FIX_SSL.md` for detailed instructions and troubleshooting.