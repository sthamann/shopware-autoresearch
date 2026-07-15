#!/usr/bin/env python3
"""Gate for VERIFY.SCALE.STOREFRONT_LISTING_TIGHT.02."""

from __future__ import annotations

import json
import subprocess
import sys
import time
import urllib.request
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SCALE_BENCH = ROOT / "verification" / "bench" / "scale" / "run_bench.sh"
REQUEST_CONFIG = ROOT / "verification" / "bench" / "request" / "config.json"
WARMUP_HTTP = ROOT / "scripts" / "warmup-http-cache.sh"
CORPUS_TARGET = 100_000
P95_THRESHOLD_MS = 150.0
WARMUP = 5
ITERATIONS = 25


def percentile(values: list[float], pct: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    idx = int(round((pct / 100.0) * (len(ordered) - 1)))
    return ordered[idx]


def timed_get(url: str) -> float:
    start = time.perf_counter()
    req = urllib.request.Request(url, method="GET", headers={"Accept": "text/html"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        resp.read()
    return (time.perf_counter() - start) * 1000.0


def main() -> int:
    subprocess.run([str(WARMUP_HTTP)], cwd=ROOT, check=False)

    scale_proc = subprocess.run(
        [str(SCALE_BENCH)], cwd=ROOT, capture_output=True, text=True, check=False
    )
    scale = json.loads(scale_proc.stdout)
    product_count = int(scale.get("product_count", 0))

    req_cfg = json.loads(REQUEST_CONFIG.read_text(encoding="utf-8"))
    category = next(r for r in req_cfg["requests"] if r["name"] == "category")
    url = req_cfg["base_url"].rstrip("/") + category["path"]

    samples: list[float] = []
    for _ in range(WARMUP):
        timed_get(url)
    for _ in range(ITERATIONS):
        samples.append(timed_get(url))

    p95_ms = percentile(samples, 95)

    gates = {
        "corpus_at_least_100k": product_count >= CORPUS_TARGET,
        "samples_collected": len(samples) >= 10,
        "category_listing_p95_tight": p95_ms <= P95_THRESHOLD_MS,
    }
    metrics = {
        "p95_ms": round(p95_ms, 2),
        "threshold_ms": P95_THRESHOLD_MS,
        "wave1_p95_ms": 184.1,
        "request_count": len(samples),
        "product_count": product_count,
    }

    ok = all(gates.values())
    report = {
        "claim_id": "VERIFY.SCALE.STOREFRONT_LISTING_TIGHT.02",
        "ts": datetime.now().astimezone().isoformat(timespec="seconds"),
        "verdict": "pass" if ok else "fail",
        "gates": gates,
        "metrics": metrics,
    }
    (HERE / "last_run.json").write_text(json.dumps(report, indent=2) + "\n")
    for name, value in gates.items():
        print(f"  gate {name}: {'PASS' if value else 'FAIL'}")
    print(f"VERIFY.SCALE.STOREFRONT_LISTING_TIGHT.02: {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
