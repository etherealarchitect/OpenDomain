#!/usr/bin/env bash
set -euo pipefail

REGION="syd"
BACKEND_APP="opendomain-api"
FRONTEND_APP="opendomain-web"
DB_NAME="opendomain-db"

echo "=== OpenDomain Fly.io Deployment ==="
echo ""

# Check flyctl is installed
if ! command -v flyctl &> /dev/null; then
    echo "Error: flyctl is not installed."
    echo "Install it with: curl -L https://fly.io/install.sh | sh"
    exit 1
fi

# Check auth
if ! flyctl auth whoami &> /dev/null; then
    echo "Not logged in. Running fly auth login..."
    flyctl auth login
fi

echo "Logged in as: $(flyctl auth whoami)"
echo ""

# Create backend app
echo "--- Creating backend app ---"
flyctl apps create "$BACKEND_APP" --machines -o personal 2>/dev/null || echo "App $BACKEND_APP already exists"

# Create frontend app
echo "--- Creating frontend app ---"
flyctl apps create "$FRONTEND_APP" --machines -o personal 2>/dev/null || echo "App $FRONTEND_APP already exists"

# Create Postgres
echo ""
echo "--- Provisioning PostgreSQL ---"
if flyctl postgres list 2>/dev/null | grep -q "$DB_NAME"; then
    echo "Postgres cluster $DB_NAME already exists"
else
    flyctl postgres create \
        --name "$DB_NAME" \
        --region "$REGION" \
        --initial-cluster-size 1 \
        --vm-size shared-cpu-1x \
        --volume-size 1
fi

# Attach Postgres to backend
echo ""
echo "--- Attaching Postgres to backend ---"
flyctl postgres attach "$DB_NAME" -a "$BACKEND_APP" 2>/dev/null || echo "Already attached"

# Set backend secrets
echo ""
echo "--- Setting backend secrets ---"
JWT_SECRET=$(openssl rand -hex 32)
flyctl secrets set \
    JWT_SECRET="$JWT_SECRET" \
    EPP_SIMULATE="true" \
    -a "$BACKEND_APP"

# Deploy backend
echo ""
echo "--- Deploying backend ---"
flyctl deploy -c fly.backend.toml --remote-only

# Deploy frontend
echo ""
echo "--- Deploying frontend ---"
flyctl deploy -c fly.frontend.toml --remote-only

echo ""
echo "=== Deployment complete ==="
echo ""
echo "Backend:  https://$BACKEND_APP.fly.dev"
echo "Frontend: https://$FRONTEND_APP.fly.dev"
echo "API Docs: https://$BACKEND_APP.fly.dev/docs"
echo ""
echo "To view logs:"
echo "  flyctl logs -a $BACKEND_APP"
echo "  flyctl logs -a $FRONTEND_APP"
