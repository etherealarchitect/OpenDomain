#!/usr/bin/env bash
# fix-vps-ssl.sh - Script to fix SSL certificate issue on VPS
# This script updates the Caddyfile with the correct domain and restarts Caddy

set -euo pipefail

echo "================================================="
echo "   OpenDomain VPS SSL Certificate Fix Script"
echo "================================================="
echo ""

# Check if we're running as root or with sudo
if [[ $EUID -eq 0 ]]; then
    echo "✓ Running as root"
else
    echo "⚠️  Not running as root. You may need to prefix commands with 'sudo'"
fi

VPS_DIR="/opt/opendomain/app"
CADDYFILE="$VPS_DIR/infrastructure/vultr/Caddyfile"
OLD_DOMAIN="opendomain.scottkbrown.com"
NEW_DOMAIN="opendomain.etherealcode.org"

echo ""
echo "Target directory: $VPS_DIR"
echo "Caddyfile: $CADDYFILE"
echo "Correcting domain: $OLD_DOMAIN → $NEW_DOMAIN"
echo ""

# 1. Check if directory exists
if [[ ! -d "$VPS_DIR" ]]; then
    echo "❌ ERROR: Directory $VPS_DIR does not exist"
    echo "Please check that OpenDomain is deployed at this location"
    exit 1
fi

# 2. Check if Caddyfile exists
if [[ ! -f "$CADDYFILE" ]]; then
    echo "❌ ERROR: Caddyfile not found at $CADDYFILE"
    exit 1
fi

echo "✓ Found Caddyfile at $CADDYFILE"
echo ""

# 3. Backup the original Caddyfile
BACKUP_FILE="$CADDYFILE.backup.$(date +%Y%m%d_%H%M%S)"
cp "$CADDYFILE" "$BACKUP_FILE"
echo "✓ Created backup: $BACKUP_FILE"
echo ""

# 4. Check current domain in Caddyfile
if grep -q "$OLD_DOMAIN" "$CADDYFILE"; then
    echo "Found old domain '$OLD_DOMAIN' in Caddyfile"
    echo ""

    # 5. Update Caddyfile with sed
    sed -i "s/$OLD_DOMAIN/$NEW_DOMAIN/g" "$CADDYFILE"

    # Verify the change
    if grep -q "$NEW_DOMAIN" "$CADDYFILE"; then
        echo "✓ Successfully updated Caddyfile to use '$NEW_DOMAIN'"
    else
        echo "❌ ERROR: Failed to update Caddyfile"
        exit 1
    fi
else
    echo "⚠️  Old domain '$OLD_DOMAIN' not found in Caddyfile"
    echo "Current content of Caddyfile block:"
    echo "---"
    head -10 "$CADDYFILE" | grep -E "^[[:alnum:]]+\.|^@|^handle"
    echo "---"
    echo ""
fi

echo ""
echo "6. Restarting Caddy service..."
echo "================================================="

# 6. Restart Caddy service using Docker Compose
cd "$VPS_DIR"

# Check if docker-compose.prod.yml exists
COMPOSE_FILE="infrastructure/vultr/docker-compose.prod.yml"
if [[ ! -f "$COMPOSE_FILE" ]]; then
    echo "❌ ERROR: Docker Compose file not found: $COMPOSE_FILE"
    exit 1
fi

echo "Found Docker Compose file: $COMPOSE_FILE"
echo ""

# Check environment file
ENV_FILE="/opt/opendomain/.env"
if [[ ! -f "$ENV_FILE" ]]; then
    echo "⚠️  WARNING: Environment file not found at $ENV_FILE"
    echo "Caddy may need email configuration for Let's Encrypt"
else
    echo "✓ Environment file found: $ENV_FILE"
    # Check if CADDY_EMAIL is set
    if grep -q "CADDY_EMAIL" "$ENV_FILE"; then
        echo "✓ CADDY_EMAIL is configured"
    else
        echo "⚠️  WARNING: CADDY_EMAIL not found in environment file"
        echo "Let's Encrypt may fail without email address"
    fi
fi

echo ""
echo "Restarting Caddy container..."
docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" restart caddy

if [[ $? -eq 0 ]]; then
    echo "✓ Caddy service restarted successfully"
else
    echo "❌ ERROR: Failed to restart Caddy service"
    echo "You may need to manually restart:"
    echo "  cd $VPS_DIR"
    echo "  docker compose --env-file /opt/opendomain/.env -f infrastructure/vultr/docker-compose.prod.yml restart caddy"
    exit 1
fi

echo ""
echo "7. Checking Caddy logs (first 10 lines)..."
echo "================================================="
sleep 5  # Give Caddy time to start
docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" logs --tail=10 caddy

echo ""
echo "8. Verifying HTTPS access..."
echo "================================================="
echo "Testing HTTPS connection to $NEW_DOMAIN..."
echo "Note: SSL certificate issuance may take a few minutes"

# Simple test with timeout
timeout 10 curl -s -o /dev/null -w "%{http_code}" "https://$NEW_DOMAIN" 2>/dev/null || true

echo ""
echo "================================================="
echo "✅ SSL Fix Complete!"
echo ""
echo "Next steps:"
echo "1. Wait 1-2 minutes for SSL certificate to be issued"
echo "2. Test the application at https://$NEW_DOMAIN"
echo "3. Check Caddy logs for any errors:"
echo "   docker compose --env-file $ENV_FILE -f $COMPOSE_FILE logs caddy"
echo "4. If SSL still fails, check Let's Encrypt rate limits"
echo "   or verify DNS propagation via: dig +short $NEW_DOMAIN"
echo ""
echo "For troubleshooting:"
echo "- Check Caddy logs: docker logs $(docker ps -q -f name=caddy)"
echo "- Verify domain resolves: nslookup $NEW_DOMAIN"
echo "- Test SSL certificate: openssl s_client -connect $NEW_DOMAIN:443"
echo "================================================="