#!/usr/bin/env python3
"""Gate for VERIFY.REQ.HOME_LISTING_PROFILE.03."""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PROFILE = ROOT / "scripts" / "profile-home.sh"
MIN_BUCKETS = 3


def main() -> int:
    proc = subprocess.run([str(PROFILE)], cwd=ROOT, capture_output=True, text=True, check=False)
    if proc.returncode != 0:
        print(proc.stderr or proc.stdout, file=sys.stderr)
        return 1

    profile = json.loads(proc.stdout)
    buckets = {
        k: v
        for k, v in profile.items()
        if k.endswith("_ms") and isinstance(v, (int, float)) and v > 0
    }

    gates = {
        "profile_ran": proc.returncode == 0,
        "at_least_three_buckets": len(buckets) >= MIN_BUCKETS,
        "home_slower_than_category": float(profile.get("home_ms", 0)) > float(profile.get("category_ms", 0)),
        "root_listing_measured": profile.get("root_listing_api_ms") is not None,
    }
    metrics = {
        "buckets": buckets,
        "profile": profile,
        "bucket_count": len(buckets),
    }

    ok = all(gates.values())
    report = {
        "claim_id": "VERIFY.REQ.HOME_LISTING_PROFILE.03",
        "ts": datetime.now().astimezone().isoformat(timespec="seconds"),
        "verdict": "pass" if ok else "fail",
        "gates": gates,
        "metrics": metrics,
    }
    (HERE / "last_run.json").write_text(json.dumps(report, indent=2) + "\n")
    for name, value in gates.items():
        print(f"  gate {name}: {'PASS' if value else 'FAIL'}")
    print(f"VERIFY.REQ.HOME_LISTING_PROFILE.03: {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
