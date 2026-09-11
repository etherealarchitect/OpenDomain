# Fix SSL Certificate Issue on VPS

## Problem

OpenDomain VPS deployment has an SSL certificate problem:
- DNS propagation is complete: `opendomain.etherealcode.org` → `108.61.169.174`
- HTTP (port 80) redirects to HTTPS (308 Permanent Redirect)  
- HTTPS (port 443) fails with error: `tlsv1 alert internal error`

**Root cause**: The Caddyfile on the VPS contains the wrong domain: `opendomain.scottkbrown.com` instead of `opendomain.etherealcode.org`.

## Solution

SSH into the VPS and update the Caddyfile with the correct domain.

### Prerequisites

1. **SSH access** to VPS with ID: `36211b65-309c-415f-9792-a290b4ebfccd`
2. **VPS IP**: `108.61.169.174`
3. **Required permissions**: Access to `/opt/opendomain/app` directory

### Step-by-Step Fix

#### Option 1: Use Automated Script (Recommended)

1. **Copy the fix script to the VPS:**

```bash
# From your local machine
scp scripts/fix-vps-ssl.sh username@108.61.169.174:/tmp/fix-vps-ssl.sh
```

2. **SSH into the VPS:**

```bash
ssh username@108.61.169.174
```

3. **Run the fix script:**

```bash
# Make script executable
chmod +x /tmp/fix-vps-ssl.sh

# Run the script
sudo /tmp/fix-vps-ssl.sh
```

#### Option 2: Manual Fix

1. **SSH into the VPS:**

```bash
ssh username@108.61.169.174
```

2. **Navigate to the deployment directory:**

```bash
cd /opt/opendomain/app
```

3. **Backup the original Caddyfile:**

```bash
cp infrastructure/vultr/Caddyfile infrastructure/vultr/Caddyfile.backup.$(date +%Y%m%d)
```

4. **Update the Caddyfile domain:**

```bash
# Update the domain from opendomain.scottkbrown.com to opendomain.etherealcode.org
sed -i 's/opendomain\.scottkbrown\.com/opendomain.etherealcode.org/g' infrastructure/vultr/Caddyfile
```

5. **Verify the change:**

```bash
grep "opendomain.etherealcode.org" infrastructure/vultr/Caddyfile
# Should show: opendomain.etherealcode.org {
```

6. **Restart the Caddy service:**

```bash
docker compose --env-file /opt/opendomain/.env -f infrastructure/vultr/docker-compose.prod.yml restart caddy
```

7. **Check Caddy logs:**

```bash
docker compose --env-file /opt/opendomain/.env -f infrastructure/vultr/docker-compose.prod.yml logs --tail=20 caddy
```

### Verify the Fix

After completing the fix:

1. **Wait 1-2 minutes** for Let's Encrypt to issue the new certificate

2. **Test HTTPS connection:**

```bash
# From your local machine
curl -I https://opendomain.etherealcode.org
```

Expected response: `HTTP/2 200` or successful connection

3. **Test the full application:**

Open in browser: https://opendomain.etherealcode.org

### Troubleshooting

#### SSL Still Failing?

1. **Check Caddy logs for errors:**

```bash
docker compose --env-file /opt/opendomain/.env -f infrastructure/vultr/docker-compose.prod.yml logs caddy
```

Look for Let's Encrypt-related errors

2. **Verify DNS propagation:**

```bash
nslookup opendomain.etherealcode.org
# Should return: 108.61.169.174
```

3. **Check SSL certificate directly:**

```bash
openssl s_client -connect opendomain.etherealcode.org:443 -servername opendomain.etherealcode.org
```

#### Common Issues

- **Rate limiting**: Let's Encrypt has rate limits (50 certificates per domain per week)
- **Network connectivity**: Ensure port 443 is open in firewall
- **Environment variables**: Verify `CADDY_EMAIL` is set in `/opt/opendomain/.env`

### Additional Configuration

If the issue persists, check these configuration files:

1. **Environment file** (`/opt/opendomain/.env`):
   ```
   OPENDOMAIN_HOSTNAME=opendomain.etherealcode.org
   CADDY_EMAIL=your-email@example.com
   ```

2. **Docker Compose status**:
   ```bash
   docker compose --env-file /opt/opendomain/.env -f infrastructure/vultr/docker-compose.prod.yml ps
   ```

All services should show `Up` status

### Rollback

If something goes wrong, restore from backup:

```bash
cd /opt/opendomain/app
cp infrastructure/vultr/Caddyfile.backup.* infrastructure/vultr/Caddyfile
docker compose --env-file /opt/opendomain/.env -f infrastructure/vultr/docker-compose.prod.yml restart caddy
```

## Monitoring

After successful SSL setup:

1. **Set up monitoring** for SSL certificate expiration
2. **Configure automatic renewal** monitoring
3. **Add uptime checks** for https://opendomain.etherealcode.org

## References

- [Caddy Documentation](https://caddyserver.com/docs/)
- [Let's Encrypt ACME](https://letsencrypt.org/how-it-works/)
- [OpenDomain Deployment Guide](DEPLOY_VULTR.md)