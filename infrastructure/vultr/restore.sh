#!/usr/bin/env bash
# Restore a PostgreSQL custom-format backup. This deliberately requires an explicit confirmation.
set -Eeuo pipefail

PROJECT_DIR=${PROJECT_DIR:-/opt/opendomain/app}
ENV_FILE=${OPENDOMAIN_ENV_FILE:-/opt/opendomain/.env}
COMPOSE_FILE="$PROJECT_DIR/infrastructure/vultr/docker-compose.prod.yml"
ARCHIVE=${1:?Usage: restore.sh /path/to/opendomain.dump}

[[ -r "$ARCHIVE" ]] || { printf 'Backup is not readable: %s\n' "$ARCHIVE" >&2; exit 1; }
[[ -r "$ENV_FILE" ]] || { printf 'Missing readable production environment file: %s\n' "$ENV_FILE" >&2; exit 1; }

set -a
# shellcheck disable=SC1090
source "$ENV_FILE"
set +a

printf 'This replaces database %s using %s. Type RESTORE to continue: ' "$POSTGRES_DB" "$ARCHIVE"
read -r confirmation
[[ "$confirmation" == "RESTORE" ]] || { printf 'Restore cancelled.\n'; exit 1; }
export OPENDOMAIN_ENV_FILE="$ENV_FILE"

cd "$PROJECT_DIR"
docker compose -f "$COMPOSE_FILE" stop backend frontend caddy
docker compose -f "$COMPOSE_FILE" exec -T db \
  pg_restore --clean --if-exists --no-owner --username="$POSTGRES_USER" --dbname="$POSTGRES_DB" < "$ARCHIVE"
docker compose -f "$COMPOSE_FILE" up -d backend frontend caddy
printf 'Restore completed. Run functional checks before reopening traffic.\n'
