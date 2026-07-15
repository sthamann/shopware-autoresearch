#!/usr/bin/env python3
"""Gate for VERIFY.SCALE.ADMIN_SEARCH_INDEX_WARM.02."""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BENCH = ROOT / "verification" / "bench" / "scale" / "run_bench.sh"
TUNE = ROOT / "scripts" / "es-tune.sh"
CORPUS_TARGET = 100_000
P95_THRESHOLD_MS = 260.0


def main() -> int:
    subprocess.run([str(TUNE)], cwd=ROOT, check=False)

    proc = subprocess.run([str(BENCH)], cwd=ROOT, capture_output=True, text=True, check=False)
    bench = json.loads(proc.stdout)
    p95_ms = float(bench.get("p95_ms", 0))
    product_count = int(bench.get("product_count", 0))

    gates = {
        "corpus_at_least_100k": product_count >= CORPUS_TARGET,
        "samples_collected": int(bench.get("request_count", 0)) >= 10,
        "admin_search_p95_after_warm": p95_ms <= P95_THRESHOLD_MS,
    }
    metrics = {
        "p95_ms": p95_ms,
        "threshold_ms": P95_THRESHOLD_MS,
        "wave1_p95_ms": 307.78,
        "product_count": product_count,
    }

    ok = all(gates.values())
    report = {
        "claim_id": "VERIFY.SCALE.ADMIN_SEARCH_INDEX_WARM.02",
        "ts": datetime.now().astimezone().isoformat(timespec="seconds"),
        "verdict": "pass" if ok else "fail",
        "gates": gates,
        "metrics": metrics,
    }
    (HERE / "last_run.json").write_text(json.dumps(report, indent=2) + "\n")
    for name, value in gates.items():
        print(f"  gate {name}: {'PASS' if value else 'FAIL'}")
    print(f"VERIFY.SCALE.ADMIN_SEARCH_INDEX_WARM.02: {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
