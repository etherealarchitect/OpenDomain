#!/usr/bin/env bash
# Create a compressed PostgreSQL backup and optionally copy it to a mounted off-host target.
set -Eeuo pipefail

PROJECT_DIR=${PROJECT_DIR:-/opt/opendomain/app}
ENV_FILE=${OPENDOMAIN_ENV_FILE:-/opt/opendomain/.env}
COMPOSE_FILE="$PROJECT_DIR/infrastructure/vultr/docker-compose.prod.yml"
BACKUP_DIR=${BACKUP_DIR:-/var/backups/opendomain}
RETENTION_DAYS=${RETENTION_DAYS:-14}

if [[ ! -r "$ENV_FILE" ]]; then
  printf 'Missing readable production environment file: %s\n' "$ENV_FILE" >&2
  exit 1
fi

set -a
# shellcheck disable=SC1090
source "$ENV_FILE"
set +a
export OPENDOMAIN_ENV_FILE="$ENV_FILE"

mkdir -p "$BACKUP_DIR"
chmod 700 "$BACKUP_DIR"
timestamp=$(date -u +%Y%m%dT%H%M%SZ)
archive="$BACKUP_DIR/opendomain-$timestamp.dump"
temp_archive="$archive.partial"

cd "$PROJECT_DIR"
docker compose -f "$COMPOSE_FILE" exec -T db \
  pg_dump --format=custom --no-owner --username="$POSTGRES_USER" "$POSTGRES_DB" > "$temp_archive"
mv "$temp_archive" "$archive"
chmod 600 "$archive"

if [[ -n ${BACKUP_DESTINATION:-} ]]; then
  install -d -m 700 "$BACKUP_DESTINATION"
  cp -p "$archive" "$BACKUP_DESTINATION/"
fi

find "$BACKUP_DIR" -type f -name 'opendomain-*.dump' -mtime "+$RETENTION_DAYS" -delete
printf 'Backup created: %s\n' "$archive"
