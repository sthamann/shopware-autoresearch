#!/usr/bin/env python3
"""Gate for VERIFY.SCALE.ADMIN_PRODUCT_SEARCH_P95.01."""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BENCH = ROOT / "verification" / "bench" / "scale" / "run_bench.sh"
CORPUS_TARGET = 100_000
P95_THRESHOLD_MS = 3000.0


def main() -> int:
    proc = subprocess.run(
        [str(BENCH)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        print(proc.stderr or proc.stdout, file=sys.stderr)
        return 1

    bench = json.loads(proc.stdout)
    p95_ms = float(bench.get("p95_ms", 0))
    request_count = int(bench.get("request_count", 0))
    product_count = int(bench.get("product_count", 0))
    corpus_ready = bool(bench.get("corpus_ready", False))

    gates = {
        "bench_ran": proc.returncode == 0,
        "corpus_at_least_100k": product_count >= CORPUS_TARGET,
        "samples_collected": request_count >= 10,
        "admin_search_p95_within_threshold": p95_ms <= P95_THRESHOLD_MS,
    }
    metrics = {
        "p95_ms": p95_ms,
        "p50_ms": bench.get("p50_ms"),
        "request_count": request_count,
        "product_count": product_count,
        "corpus_target": CORPUS_TARGET,
        "corpus_ready": corpus_ready,
        "threshold_ms": P95_THRESHOLD_MS,
        "missing_capability": (
            None
            if corpus_ready
            else f"100k product corpus not seeded (current={product_count})"
        ),
    }

    ok = all(gates.values())
    report = {
        "claim_id": "VERIFY.SCALE.ADMIN_PRODUCT_SEARCH_P95.01",
        "ts": datetime.now().astimezone().isoformat(timespec="seconds"),
        "verdict": "pass" if ok else "fail",
        "gates": gates,
        "metrics": metrics,
    }
    (HERE / "last_run.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    for name, value in gates.items():
        print(f"  gate {name}: {'PASS' if value else 'FAIL'}")
    print(f"VERIFY.SCALE.ADMIN_PRODUCT_SEARCH_P95.01: {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
