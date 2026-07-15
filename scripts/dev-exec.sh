#!/usr/bin/env bash
set -euo pipefail

source "$(dirname "${BASH_SOURCE[0]}")/dev-compose.sh"
cd "${ROOT}"

if [[ $# -eq 0 ]]; then
  echo "Usage: $0 <command...>" >&2
  echo "Example: $0 composer setup" >&2
  exit 1
fi

docker compose -f "${COMPOSE_BASE}" -f "${COMPOSE_OVERRIDE}" exec web "$@"
