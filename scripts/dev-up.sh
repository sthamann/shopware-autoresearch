#!/usr/bin/env bash
set -euo pipefail

source "$(dirname "${BASH_SOURCE[0]}")/dev-compose.sh"
cd "${ROOT}"

echo "==> Starting Shopware Docker stack (trunk / latest dev image)"
docker compose -f "${COMPOSE_BASE}" -f "${COMPOSE_OVERRIDE}" up -d

echo "==> Stack status"
docker compose -f "${COMPOSE_BASE}" -f "${COMPOSE_OVERRIDE}" ps

echo ""
echo "Shopware:     http://localhost:8000"
echo "Adminer:      http://localhost:9080"
echo "Mailpit:      http://localhost:8025"
echo ""
echo "First-time setup (inside container): ./scripts/dev-setup.sh"
