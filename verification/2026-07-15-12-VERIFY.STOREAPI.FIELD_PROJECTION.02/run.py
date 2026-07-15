#!/usr/bin/env python3
"""Gate for VERIFY.STOREAPI.FIELD_PROJECTION.02."""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BENCH = ROOT / "verification" / "bench" / "api" / "run_bench.sh"
P95_THRESHOLD_MS = 80.0


def main() -> int:
    subprocess.run(
        [str(ROOT / "scripts" / "dev-exec.sh"), "bin/console", "cache:clear"],
        cwd=ROOT,
        check=False,
    )

    proc = subprocess.run([str(BENCH)], cwd=ROOT, capture_output=True, text=True, check=False)
    bench = json.loads(proc.stdout)
    p95_ms = float(bench.get("p95_ms", 0))

    gates = {
        "bench_ran": proc.returncode == 0,
        "samples_collected": int(bench.get("request_count", 0)) >= 10,
        "store_api_p95_projected": p95_ms <= P95_THRESHOLD_MS,
    }
    metrics = {
        "p95_ms": p95_ms,
        "threshold_ms": P95_THRESHOLD_MS,
        "wave1_p95_ms": 110.3,
        "by_endpoint": bench.get("by_endpoint"),
    }

    ok = all(gates.values())
    report = {
        "claim_id": "VERIFY.STOREAPI.FIELD_PROJECTION.02",
        "ts": datetime.now().astimezone().isoformat(timespec="seconds"),
        "verdict": "pass" if ok else "fail",
        "gates": gates,
        "metrics": metrics,
    }
    (HERE / "last_run.json").write_text(json.dumps(report, indent=2) + "\n")
    for name, value in gates.items():
        print(f"  gate {name}: {'PASS' if value else 'FAIL'}")
    print(f"VERIFY.STOREAPI.FIELD_PROJECTION.02: {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
