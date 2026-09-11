#!/usr/bin/env bash
# Deploy an already reviewed OpenDomain revision on a prepared Vultr host.
set -Eeuo pipefail

PROJECT_DIR=${PROJECT_DIR:-/opt/opendomain/app}
ENV_FILE=${OPENDOMAIN_ENV_FILE:-/opt/opendomain/.env}
COMPOSE_FILE="$PROJECT_DIR/infrastructure/vultr/docker-compose.prod.yml"
REF=${1:?Usage: deploy.sh <immutable-git-ref>}

if [[ ! -r "$ENV_FILE" ]]; then
  printf 'Missing readable production environment file: %s\n' "$ENV_FILE" >&2
  exit 1
fi
if [[ $(stat -f '%Lp' "$ENV_FILE") != 600 ]]; then
  printf 'Refusing to use %s: permissions must be 0600.\n' "$ENV_FILE" >&2
  exit 1
fi

cd "$PROJECT_DIR"
git fetch --tags origin
git checkout --detach "$REF"

# Compose interpolation requires these variables in its process environment.
set -a
# shellcheck disable=SC1090
source "$ENV_FILE"
set +a

export OPENDOMAIN_ENV_FILE="$ENV_FILE"
export OPEN_DOMAIN_IMAGE_TAG="${REF:0:12}"

docker compose -f "$COMPOSE_FILE" config --quiet
docker compose -f "$COMPOSE_FILE" build --pull backend frontend
docker compose -f "$COMPOSE_FILE" up -d db redis
docker compose -f "$COMPOSE_FILE" run --rm migrate
docker compose -f "$COMPOSE_FILE" up -d --remove-orphans backend frontend caddy

docker compose -f "$COMPOSE_FILE" ps
printf 'Deployed %s. Validate HTTPS and the complete auth flow before DNS cutover.\n' "$REF"
