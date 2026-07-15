#!/usr/bin/env bash
set -euo pipefail

source "$(dirname "${BASH_SOURCE[0]}")/dev-compose.sh"
cd "${ROOT}"

echo "==> Running Shopware composer setup inside web container (may take several minutes)"
docker compose -f "${COMPOSE_BASE}" -f "${COMPOSE_OVERRIDE}" exec web composer setup

echo "==> Shopware setup complete"
echo "Storefront: http://localhost:8000"
echo "Admin:      http://localhost:8000/admin (admin / shopware)"
