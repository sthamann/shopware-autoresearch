#!/usr/bin/env bash
# Warm Symfony app cache (container + pools) before request-perf measurement.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

"${ROOT}/scripts/dev-exec.sh" bin/console cache:warmup --no-optional-warmers >/dev/null
"${ROOT}/scripts/dev-exec.sh" bin/console cache:pool:clear cache.object >/dev/null 2>&1 || true
"${ROOT}/scripts/dev-exec.sh" bin/console cache:warmup --no-optional-warmers >/dev/null

echo "App cache warmed"
