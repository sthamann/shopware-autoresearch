#!/usr/bin/env python3
"""Gate for VERIFY.REQ.HOME_LISTING_DEFER.04."""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BENCH = ROOT / "verification" / "bench" / "request" / "run_bench.sh"
SCALE_BENCH = ROOT / "verification" / "bench" / "scale" / "run_bench.sh"
HOME_THRESHOLD_MS = 500.0
WAVE3_HOME_MS = 3199.0
CORPUS_TARGET = 100_000


def main() -> int:
    scale_proc = subprocess.run([str(SCALE_BENCH)], cwd=ROOT, capture_output=True, text=True, check=False)
    scale = json.loads(scale_proc.stdout) if scale_proc.returncode == 0 else {}
    product_count = int(scale.get("product_count", 0))

    proc = subprocess.run([str(BENCH)], cwd=ROOT, capture_output=True, text=True, check=False)
    bench = json.loads(proc.stdout)
    by_request = bench.get("by_request") or {}
    home_p95 = float(by_request.get("home", {}).get("p95_ms", bench.get("p95_ms", 0)))

    gates = {
        "bench_ran": proc.returncode == 0,
        "corpus_at_least_100k": product_count >= CORPUS_TARGET,
        "home_p95_deferred": home_p95 <= HOME_THRESHOLD_MS,
        "home_improved_vs_wave3": home_p95 < WAVE3_HOME_MS,
    }
    metrics = {
        "home_p95_ms": home_p95,
        "wave3_home_p95_ms": WAVE3_HOME_MS,
        "delta_ms": round(home_p95 - WAVE3_HOME_MS, 2),
        "threshold_ms": HOME_THRESHOLD_MS,
        "product_count": product_count,
        "by_request": by_request,
    }

    ok = all(gates.values())
    report = {
        "claim_id": "VERIFY.REQ.HOME_LISTING_DEFER.04",
        "ts": datetime.now().astimezone().isoformat(timespec="seconds"),
        "verdict": "pass" if ok else "fail",
        "gates": gates,
        "metrics": metrics,
    }
    (HERE / "last_run.json").write_text(json.dumps(report, indent=2) + "\n")
    for name, value in gates.items():
        print(f"  gate {name}: {'PASS' if value else 'FAIL'}")
    print(f"VERIFY.REQ.HOME_LISTING_DEFER.04: {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
