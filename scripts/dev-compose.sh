#!/usr/bin/env bash
# Resolve compose file paths for the multirepo root.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
COMPOSE_BASE="${ROOT}/repos/shopware/compose.yaml"
COMPOSE_OVERRIDE="${ROOT}/compose.override.yaml"

if [[ ! -f "${COMPOSE_BASE}" ]]; then
  echo "Missing ${COMPOSE_BASE}. Run: git submodule update --init --recursive" >&2
  exit 1
fi

export ROOT COMPOSE_BASE COMPOSE_OVERRIDE
