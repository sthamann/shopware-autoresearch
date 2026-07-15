#!/usr/bin/env bash
# Warm Symfony HTTP cache for fixed request-perf URLs.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CONFIG="${ROOT}/verification/bench/request/config.json"
BASE_URL="$(python3 -c "import json; print(json.load(open('${CONFIG}'))['base_url'].rstrip('/'))")"

"${ROOT}/scripts/dev-exec.sh" bin/console cache:clear:http >/dev/null 2>&1 || true

while IFS= read -r path; do
  curl -sS -o /dev/null -H 'Accept: text/html' "${BASE_URL}${path}" || true
  curl -sS -o /dev/null -H 'Accept: text/html' "${BASE_URL}${path}" || true
done < <(python3 -c "
import json
for req in json.load(open('${CONFIG}'))['requests']:
    print(req['path'])
")

echo "HTTP cache warmed for ${BASE_URL}"
