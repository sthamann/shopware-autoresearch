#!/usr/bin/env bash
# Refresh product search index before scale admin-search bench.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

"${ROOT}/scripts/dev-exec.sh" bin/console dal:refresh:index --only product --no-interaction >/dev/null
echo "Product index refreshed"
