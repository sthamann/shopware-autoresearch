#!/usr/bin/env bash
set -euo pipefail

source "$(dirname "${BASH_SOURCE[0]}")/dev-compose.sh"
cd "${ROOT}"

docker compose -f "${COMPOSE_BASE}" -f "${COMPOSE_OVERRIDE}" down "$@"
