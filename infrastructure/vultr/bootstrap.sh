#!/bin/bash
# Initialize and configure an OpenDomain VPS on Ubuntu 24.04
set -Eeuo pipefail

# 1. System update and basic tools
apt-get update
apt-get install -y docker.io docker-compose-plugin curl fail2ban ufw

# 2. Create opendomain user
useradd -m -s /bin/bash opendomain
usermod -aG docker opendomain

# 3. Setup UFW firewall
ufw default deny incoming
ufw default allow outgoing
ufw allow 80/tcp comment 'HTTP'
ufw allow 443/tcp comment 'HTTPS'
ufw allow 22/tcp comment 'SSH'
ufw enable

# 4. Create data directories
mkdir -p /opt/opendomain/{db,redis,caddy}
chown -R opendomain:opendomain /opt/opendomain

# 5. Deploy docker-compose
cd /opt/opendomain/app
cp infrastructure/vultr/docker-compose.prod.yml /opt/opendomain/docker-compose.yml
export OPENDOMAIN_ENV_FILE=/opt/opendomain/.env
docker compose pull db redis
docker compose up -d db redis

# 6. Wait for database
sleep 10

# 7. Run migrations
docker compose run --rm migrate

# 8. Start services
docker compose up -d backend frontend caddy

# 9. Enable fail2ban
systemctl enable fail2ban
systemctl start fail2ban

echo "OpenDomain deployment complete. Validate at HTTPS://<server-ip>"