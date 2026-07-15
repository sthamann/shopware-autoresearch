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

# verification/bench is harness-owned, not a claim folder — teach scan to skip it
# until upstream pawl adds "bench" to SKIP_DIRS (tools/lib/ledger.py).
python3 - <<'PY'
from pathlib import Path

ledger = Path("pawl/tools/lib/ledger.py")
text = ledger.read_text(encoding="utf-8")
needle = 'SKIP_DIRS = {"_template", "memory", "autoresearch", "lib", "__pycache__"}'
replacement = 'SKIP_DIRS = {"_template", "memory", "autoresearch", "lib", "__pycache__", "bench"}'
if '"bench"' not in text and needle in text:
    ledger.write_text(text.replace(needle, replacement), encoding="utf-8")
    print("patched pawl scan to skip verification/bench/")
PY

echo "==> Done. Next: ./scripts/dev-up.sh"
