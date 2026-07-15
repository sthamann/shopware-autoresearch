#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT}"

echo "==> Initializing git submodules"
git submodule update --init --recursive

echo "==> Bootstrapping Pawl verification (idempotent)"
python3 pawl/tools/init_project.py auto-research-shopware \
  --plans-dir docs/plans \
  --verification-dir verification

echo "==> Done. Next: ./scripts/dev-up.sh"
