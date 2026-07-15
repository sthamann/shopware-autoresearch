#!/usr/bin/env python3
"""Gate for VERIFY.CACHE.OPCACHE_WARMUP.01."""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BENCH = ROOT / "verification" / "bench" / "request" / "run_bench.sh"
WARMUP = ROOT / "scripts" / "warmup-app-cache.sh"
P95_THRESHOLD_MS = 180.0
BASELINE_MS = 195.0


def main() -> int:
    subprocess.run([str(WARMUP)], cwd=ROOT, check=False)

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

    gates = {
        "bench_ran": proc.returncode == 0,
        "samples_collected": request_count >= 10,
        "home_p95_after_warmup": p95_ms <= P95_THRESHOLD_MS,
    }
    metrics = {
        "p95_ms": p95_ms,
        "p50_ms": bench.get("p50_ms"),
        "baseline_ms": BASELINE_MS,
        "threshold_ms": P95_THRESHOLD_MS,
        "request_count": request_count,
        "by_request": bench.get("by_request"),
    }

    ok = all(gates.values())
    report = {
        "claim_id": "VERIFY.CACHE.OPCACHE_WARMUP.01",
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
    print(f"VERIFY.CACHE.OPCACHE_WARMUP.01: {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
