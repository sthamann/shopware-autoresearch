#!/usr/bin/env python3
"""Gate for VERIFY.REQ.HOME_DEV_OVERHEAD.02."""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BENCH = ROOT / "verification" / "bench" / "request" / "run_bench.sh"
PROFILE = ROOT / "scripts" / "profile-home.sh"
HOME_THRESHOLD_MS = 500.0
CATEGORY_THRESHOLD_MS = 250.0
WAVE2_HOME_MS = 3086.92


def main() -> int:
    profile_proc = subprocess.run([str(PROFILE)], cwd=ROOT, capture_output=True, text=True, check=False)
    profile = json.loads(profile_proc.stdout) if profile_proc.returncode == 0 else {}

    proc = subprocess.run([str(BENCH)], cwd=ROOT, capture_output=True, text=True, check=False)
    bench = json.loads(proc.stdout)
    by_request = bench.get("by_request") or {}
    home_p95 = float(by_request.get("home", {}).get("p95_ms", bench.get("p95_ms", 0)))
    category_p95 = float(by_request.get("category", {}).get("p95_ms", 0))
    ratio = round(home_p95 / category_p95, 2) if category_p95 else 0.0

    gates = {
        "bench_ran": proc.returncode == 0,
        "home_p95_bounded": home_p95 <= HOME_THRESHOLD_MS,
        "category_p95_healthy": category_p95 <= CATEGORY_THRESHOLD_MS,
        "home_not_10x_category": ratio <= 10.0,
    }
    metrics = {
        "home_p95_ms": home_p95,
        "category_p95_ms": category_p95,
        "home_to_category_ratio": ratio,
        "wave2_home_p95_ms": WAVE2_HOME_MS,
        "home_delta_ms": round(home_p95 - WAVE2_HOME_MS, 2),
        "home_threshold_ms": HOME_THRESHOLD_MS,
        "profile": profile,
        "by_request": by_request,
    }

    ok = all(gates.values())
    report = {
        "claim_id": "VERIFY.REQ.HOME_DEV_OVERHEAD.02",
        "ts": datetime.now().astimezone().isoformat(timespec="seconds"),
        "verdict": "pass" if ok else "fail",
        "gates": gates,
        "metrics": metrics,
    }
    (HERE / "last_run.json").write_text(json.dumps(report, indent=2) + "\n")
    for name, value in gates.items():
        print(f"  gate {name}: {'PASS' if value else 'FAIL'}")
    print(f"VERIFY.REQ.HOME_DEV_OVERHEAD.02: {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
